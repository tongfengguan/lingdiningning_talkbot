# 🌸 NingNing-Bot (绫地宁宁 AI 助手)

基于 **Python 3.13** + **DeepSeek-V3** + **NapCatQQ** 构建的高度还原向 AI 机器人。  
深度复刻《魔女的夜宴》女主角 **绫地宁宁 (Ayachi Nene)** 的双重人格与技术宅属性。

---

## 🌟 核心特性

- **🎭 灵魂级人设**：复刻宁宁的“高冷偶像/爱吐槽少女”双重人格，自带 (脸红)、(叹气) 等神态描写。
- **🧠 超强 RAG 记忆 (Vector Memory)**：集成基于阿里 DashScope 的向量数据库。宁宁不仅能秒读百页 PDF，还能记住你们几个月前聊过的往事。
- **📚 本地知识库 (PDF Search)**：支持对 `assets/docs/` 下的 PDF 进行语义检索，宁宁会结合文档内容回答专业问题。
- **🌐 实时联网 (Web Search)**：AI 会自主判断是否需要“联网观测”实时动态。
- **🖼️ 智能表情包系统**：支持 `[表情: 名字]` 触发、自动搜图下载以及 `/学这个` 调教功能。
- **📧 真实邮件投递**：支持 SMTP 协议发送代码模板或长信。
- **📊 Codeforces 监控**：内置 `/cf [handle]` 指令，实时抓取 CF 战绩。
- **🚀 一键穿透**：集成 Cloudflare Tunnel，无需公网 IP 即可联动。

---

## 📂 项目架构

```text
Talkbot/
├── engine/                 # 逻辑驱动核心 (各功能均拥有独立命名空间)
│   ├── aiEngine/           # AI 决策核心 (支持视觉/RAG)
│   ├── ragEngine/          # 向量检索引擎 [NEW]
│   ├── pdfEngine/          # PDF 解析与同步
│   ├── memoryManager/      # SQLite + 向量长效记忆
│   ├── emailEngine/        # SMTP 邮件系统
│   ├── cfEngine/           # Codeforces 插件
│   ├── searchEngine/       # Web 搜索与图片抓取
│   ├── imageUtils/         # 图片处理与视觉识别
│   ├── messageUtils/       # 模拟打字逻辑
│   └── qqAdapter/          # OneBot11 协议适配器
├── assets/
│   ├── images/             # 表情包
│   └── docs/               # PDF 文档库
├── data/                   # 数据库与向量存储
├── main.py                 # 入口 (FastAPI + MonkeyPatch)
├── config.py               # 统一配置加载
└── start.bat               # 启动脚本
```

---

## 🚀 快速开始

1.  **环境**：Python 3.13+。
2.  **配置**：在 `.env` 中填入 `DEEPSEEK_API_KEY` 和 `DASHSCOPE_API_KEY`（用于视觉和向量记忆）。
3.  **运行**：双击 `start.bat`。宁宁会在启动时自动扫描并索引 `assets/docs/` 下的新 PDF。

---

## 💬 常用操作

- **深度问答**："宁宁，我记得我以前和你说过我喜欢什么，你还记得吗？"
- **文档阅读**："帮我看看文档里关于 XXX 的原理是怎么说的。"
- **技能演示**：直接发图、查 CF、教表情包。

---

## ⚖️ 免责声明
本项目仅供技术研究。请确保在遵守相关法律法规的前提下运行。

*“哈啊……居然让我记这么多东西，你是笨蛋吗？”*
