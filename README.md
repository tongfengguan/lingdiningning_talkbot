# 🌸 NingNing-Bot (绫地宁宁 AI 助手) 完整部署手册

本项目是一个基于 **Python 3.13** + **DeepSeek-V3** + **NapCatQQ** 构建的高度还原向 AI 机器人。  
深度复刻《魔女的夜宴》女主角 **绫地宁宁 (Ayachi Nene)** 的双重人格、技术宅属性以及魔女背景。

---

## 🌟 核心能力

1.  **🎭 灵魂级人设**：基于 0 路线 True End 后的宁宁进行建模，具备（脸红）、（键盘敲击声）等远程聊天神态描写。
2.  **🧠 RAG 超长记忆**：集成基于阿里 DashScope 的向量数据库，宁宁能记住数月前的聊天细节。
3.  **📚 知识库搜索**：支持对 `assets/docs/` 下的 **PDF/TXT/MD** 进行语义检索，宁宁能帮你读文档、写代码。
4.  **👁️ 魔女之眼 (视觉)**：接入阿里 Qwen-VL 视觉模型，能看懂你发的表情包、代码截图，并进行毒舌点评。
5.  **📺 B 站热门联动**：实时抓取 B 站热门视频，自动展示**封面图**及**播放/点赞/投币/收藏**等硬核数据。
6.  **📧 真实邮件投递**：支持通过 SMTP 发送真实邮件（代码模板、告白信等），具备多端口兼容性。
7.  **📊 技术宅插件**：内置 Codeforces 战绩查询 (`/cf`) 及自动搜图/教学功能。
8.  **💻 开发者仪表盘**：内置 Web UI (`/dashboard`)，实时监控宁宁的记忆与系统状态。

---

## 🛠️ 第一步：准备工作

在开始之前，你需要准备好以下“原料”：

1.  **Python 环境**：安装 [Python 3.13+](https://www.python.org/)。
2.  **API 密钥**：
    *   **DeepSeek Key**：[点击获取](https://platform.deepseek.com/)（用于大脑思考）。
    *   **DashScope Key**：[点击获取](https://dashscope.console.aliyun.com/)（用于视觉和 RAG 记忆）。
3.  **邮箱授权码**：如果你需要发邮件功能，去 QQ 邮箱设置中开启 `POP3/SMTP` 并获取 16 位授权码。
4.  **NapCatQQ**：下载并运行 [NapCatQQ](https://github.com/NapNeko/NapCatQQ)（用于连接 QQ）。

---

## 🚀 第二步：部署流程

### 1. 克隆与环境安装
```powershell
# 进入项目目录
cd Talkbot

# 创建并激活虚拟环境
python -m venv venv
.\venv\Scripts\activate

# 安装所有依赖包
pip install -r requirements.txt
```

### 2. 配置环境变量
在项目根目录新建 `.env` 文件，内容如下（**务必不要上传此文件到 Git**）：
```env
# 核心配置
DEEPSEEK_API_KEY=你的DeepSeek_Key
DASHSCOPE_API_KEY=你的阿里灵积_Key
BOT_NAME=绫地宁宁
BOT_PORT=8080

# QQ 配置
ADMIN_QQ=你的主号QQ
NAPCAT_URL=http://localhost:3000

# 邮件配置 (可选)
SMTP_USER=机器人的邮箱@qq.com
SMTP_PASSWORD=16位授权码
RECEIVER_EMAIL=你的主号邮箱@qq.com
```

### 3. 准备知识库
*   **文档**：将你想让宁宁学习的资料（如算法笔记）放入 `assets/docs/`。
*   **图片**：将初始表情包放入 `assets/images/`，命名如 `亲亲.jpg`。

---

## 🎮 运行与联动

### 1. 启动 Bot
双击运行根目录下的 `start.bat`。它会启动两个窗口：
*   **NingNing_Bot**：核心程序。启动时会提示 `正在学习新文档...`，说明 RAG 引擎正在工作。
*   **CF_Tunnel**：内网穿透。请注意此窗口输出的 `https://xxx.trycloudflare.com` 地址。

### 2. 配置 NapCatQQ
打开 NapCat 管理后台（默认 `localhost:6099`）：
1.  **HTTP 服务 (Server)**：开启，端口设为 `3000`。
2.  **HTTP Client (回调)**：添加新地址：`穿透窗口生成的地址/qq/webhook`。
    *   *例如：https://my-bot-url.trycloudflare.com/qq/webhook*

### 3. 使用开发者仪表盘
在浏览器访问：`http://localhost:8080/dashboard`
*   你可以实时查看宁宁最近生成的**向量记忆**以及**已学习的文档列表**。

---

## 💬 互动指令汇总

| 动作 | 指令/方式 | 备注 |
| :--- | :--- | :--- |
| **正常聊天** | 直接发消息 | 宁宁会根据心情随机触发 RAG 记忆或联网搜索 |
| **看 B 站热门** | "宁宁，B站有啥好看的？" | 自动展示封面、三连数据及专属点评 |
| **查询 CF** | `/cf 用户名` | 实时拉取 Codeforces Rating 战绩 |
| **调教表情包** | 发图并回复 `/学这个 名字` | 宁宁会将此图永久存入私房图库 |
| **发邮件** | "宁宁，发个线段树模板到我邮箱" | 触发真实邮件投递 (需配置 SMTP) |
| **识图** | 发送任何图片 | 宁宁会自动通过“魔女之眼”进行分析 |
| **清空上下文** | `/清除记忆` | 让宁宁暂时忘记当前对话，重新开始 |

---

## 📂 项目结构
```text
Talkbot/
├── engine/                 # 功能驱动文件夹
│   ├── aiEngine/           # DeepSeek 对话与决策
│   ├── ragEngine/          # Numpy 向量检索引擎
│   ├── biliEngine/         # B 站数据抓取
│   ├── pdfEngine/          # 文档解析与同步
│   ├── memoryManager/      # SQLite + 向量长效记忆
│   ├── imageUtils/         # 图片处理与识图
│   ├── dashboard/          # 可视化控制台
│   └── qqAdapter/          # QQ 接口协议适配
├── assets/                 # 静态资源 (docs/ images/)
├── data/                   # 数据库与向量存储
├── config.py               # 环境变量加载
└── main.py                 # FastAPI 入口与定时任务
```

---

## ⚖️ 免责声明
本项目仅供个人学习及技术研究。请确保在遵守相关法律法规的前提下运行。

*“哈啊……说明书写得这么详细你还不会用的话，就真的是无可救药的笨蛋了呢。”*
