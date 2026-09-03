[README.md](https://github.com/user-attachments/files/31793320/README.md)
# AI Scientist研究自动化系统

基于大模型的多智能体科研工作流：提交一个研究问题，系统自动完成「问题拆解 → 联网文献调研 → 假设生成 → 批判评审 → 报告撰写 → 参考文献核验」，产出一份结构规范、引用可核验的《科学假设与研究计划》，并支持参考文献的人工复核。当前以 AIGC 文本检测为验证场景。

## 运行

```bash
pip install -r logs/requirements.txt
cp .env.example .env        # 填入 DEEPSEEK_API_KEY=sk-...
python web_app.py           # → http://127.0.0.1:8000
```

也支持 CLI 模式（`python -m logs.main`）和 Docker 部署（`docker compose up -d`）。

## 依赖

- Python 3.10+
- `openai`、`python-dotenv`（见 `logs/requirements.txt`）
- 一个大模型 API Key（DeepSeek 或阿里云百炼 Qwen，OpenAI 兼容协议）

## 入口

| 入口 | 说明 |
|---|---|
| `web_app.py` | Web 服务与流水线编排 |
| `agents/` | 六个智能体（规划 / 检索 / 假设 / 评审 / 写作 / 核验） |
| `logs/bailian_client.py` | 统一模型调用入口（可在此切换底座模型） |
| `frontend/index.html` | 单页面前端（进度轮询 + 人工复核面板） |

生成的研究计划与核验报告输出到 `logs/outputs/`。
