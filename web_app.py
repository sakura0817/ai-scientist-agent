import json
import os
import threading
import traceback
import uuid
from datetime import datetime
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse


BASE_DIR = Path(__file__).resolve().parent
LOGS_DIR = BASE_DIR / "logs"
FRONTEND_DIR = BASE_DIR / "frontend"
OUTPUTS_DIR = LOGS_DIR / "outputs"

os.chdir(LOGS_DIR)
import sys

sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(LOGS_DIR))

from agents.critic import run_critic
from agents.hypothesis import run_hypothesis_generator
from agents.planner import run_planner
from agents.reference_checker import run_reference_checker
from agents.report import run_report_writer
from agents.search_miner import run_search_miner


jobs = {}
jobs_lock = threading.Lock()


def now():
    return datetime.now().isoformat(timespec="seconds")


def public_path(path):
    try:
        return str(path.resolve())
    except OSError:
        return str(path)


def update_job(job_id, **changes):
    with jobs_lock:
        job = jobs[job_id]
        job.update(changes)
        job["updated_at"] = now()


def set_result(job_id, key, value):
    with jobs_lock:
        job = jobs[job_id]
        job.setdefault("results", {})[key] = value
        job["updated_at"] = now()


def snapshot_job(job_id):
    with jobs_lock:
        job = jobs.get(job_id)
        if not job:
            return None
        return json.loads(json.dumps(job, ensure_ascii=False))


def run_pipeline(job_id, research_question):
    try:
        update_job(job_id, status="running", current_step="planner", message="Research Planner 正在拆解问题")
        planner_result = run_planner(research_question)
        set_result(job_id, "planner", planner_result)

        update_job(job_id, current_step="evidence", message="Web Search Miner 正在联网搜索和整理证据")
        evidence = run_search_miner(research_question, planner_result)
        set_result(job_id, "evidence", evidence)

        update_job(job_id, current_step="hypotheses", message="Hypothesis Generator 正在生成候选假设")
        hypotheses = run_hypothesis_generator(research_question, evidence)
        set_result(job_id, "hypotheses", hypotheses)

        update_job(job_id, current_step="critique", message="Critic Reviewer 正在评审候选假设")
        critique = run_critic(research_question, evidence, hypotheses)
        set_result(job_id, "critique", critique)

        update_job(job_id, current_step="report", message="Report Writer 正在生成研究计划")
        report = run_report_writer(research_question, evidence, hypotheses, critique)
        set_result(job_id, "report", report)

        update_job(job_id, current_step="reference_check", message="Reference Checker 正在联网核验参考文献")
        reference_check = run_reference_checker(research_question, evidence, report)
        set_result(job_id, "reference_check", reference_check)

        final_report = report + "\n\n---\n\n# Reference Check\n\n" + reference_check
        set_result(job_id, "final", final_report)

        OUTPUTS_DIR.mkdir(exist_ok=True)
        report_path = OUTPUTS_DIR / "research_plan.md"
        check_path = OUTPUTS_DIR / "reference_check.md"
        final_path = OUTPUTS_DIR / "research_plan_with_check.md"

        report_path.write_text(report, encoding="utf-8")
        check_path.write_text(reference_check, encoding="utf-8")
        final_path.write_text(final_report, encoding="utf-8")

        update_job(
            job_id,
            status="done",
            current_step="final",
            message="全部完成",
            output_paths={
                "research_plan.md": public_path(report_path),
                "reference_check.md": public_path(check_path),
                "research_plan_with_check.md": public_path(final_path),
            },
        )
    except Exception as exc:
        update_job(
            job_id,
            status="failed",
            error=str(exc),
            traceback=traceback.format_exc(),
        )


class AppHandler(SimpleHTTPRequestHandler):
    server_version = "AIScientistMVP/0.1"

    def log_message(self, format, *args):
        print("%s - %s" % (self.address_string(), format % args))

    def send_json(self, payload, status=200):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def send_text(self, text, status=200, content_type="text/plain; charset=utf-8"):
        body = text.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = unquote(parsed.path)

        if path == "/" or path == "/index.html":
            self.serve_file(FRONTEND_DIR / "index.html", "text/html; charset=utf-8")
            return

        if path.startswith("/api/jobs/"):
            job_id = path.removeprefix("/api/jobs/").strip("/")
            job = snapshot_job(job_id)
            if not job:
                self.send_json({"error": "job not found"}, status=404)
                return
            self.send_json(job)
            return

        self.send_json({"error": "not found"}, status=404)

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path != "/api/run":
            self.send_json({"error": "not found"}, status=404)
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length).decode("utf-8")
            payload = json.loads(raw or "{}")
            question = str(payload.get("question", "")).strip()
        except Exception:
            self.send_json({"error": "invalid json body"}, status=400)
            return

        if not question:
            self.send_json({"error": "question is required"}, status=400)
            return

        job_id = uuid.uuid4().hex
        with jobs_lock:
            jobs[job_id] = {
                "job_id": job_id,
                "question": question,
                "status": "queued",
                "current_step": "planner",
                "message": "任务已创建",
                "results": {},
                "output_paths": {},
                "created_at": now(),
                "updated_at": now(),
            }

        worker = threading.Thread(target=run_pipeline, args=(job_id, question), daemon=True)
        worker.start()
        self.send_json({"job_id": job_id, "status": "queued"}, status=202)

    def serve_file(self, path, content_type):
        try:
            body = path.read_bytes()
        except FileNotFoundError:
            self.send_json({"error": "file not found"}, status=404)
            return

        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)


def main():
    host = os.getenv("AI_SCIENTIST_HOST", "127.0.0.1")
    port = int(os.getenv("AI_SCIENTIST_PORT", "8000"))
    server = ThreadingHTTPServer((host, port), AppHandler)
    print(f"AI Scientist MVP web app running at http://{host}:{port}")
    print("Press Ctrl+C to stop.")
    server.serve_forever()


if __name__ == "__main__":
    main()
