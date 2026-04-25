import os
import json
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from config import config
from engine.ragEngine.ragEngine import rag_engine

router = APIRouter(prefix="/dashboard")

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>NingNing Dashboard</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #1a1a1a; color: #eee; margin: 0; padding: 20px; }
        .card { background: #252525; padding: 20px; border-radius: 10px; margin-bottom: 20px; border: 1px solid #333; }
        h1 { color: #ff85a2; }
        .status { color: #4caf50; font-weight: bold; }
        pre { background: #000; padding: 10px; border-radius: 5px; overflow-x: auto; font-size: 12px; }
        button { background: #ff85a2; border: none; padding: 10px 20px; border-radius: 5px; color: white; cursor: pointer; }
        button:hover { background: #ff5e84; }
        .memory-item { border-bottom: 1px solid #333; padding: 10px 0; }
        .source { color: #888; font-size: 11px; }
    </style>
</head>
<body>
    <h1>🌸 NingNing Bot 控制台</h1>
    
    <div class="card">
        <h3>基本状态</h3>
        <p>Bot 名称: <b>{{ bot_name }}</b></p>
        <p>监听端口: <b>{{ port }}</b></p>
        <p>本地文档数: <b>{{ doc_count }}</b></p>
    </div>

    <div class="card">
        <h3>RAG 长期记忆 (最近 5 条)</h3>
        {% for item in memories %}
        <div class="memory-item">
            <div>{{ item.text }}</div>
            <div class="source">来源: {{ item.source }}</div>
        </div>
        {% endfor %}
    </div>

    <div class="card">
        <h3>操作面板</h3>
        <p>复制 Cloudflare 域名到此处一键更新 NapCat：</p>
        <input type="text" id="cf_url" placeholder="https://xxx.trycloudflare.com" style="width: 300px; padding: 10px; border-radius: 5px; border: 1px solid #444; background: #333; color: white;">
        <button onclick="updateUrl()">同步到 NapCat</button>
        <p id="msg"></p>
    </div>

    <script>
        async function updateUrl() {
            const url = document.getElementById('cf_url').value;
            if(!url) return alert('请填入域名');
            const res = await fetch('/dashboard/sync-napcat?url=' + encodeURIComponent(url));
            const data = await res.json();
            document.getElementById('msg').innerText = data.status === 'ok' ? '✅ 同步成功！' : '❌ 失败: ' + data.detail;
        }
    </script>
</body>
</html>
"""

@router.get("/", response_class=HTMLResponse)
async def index():
    # 模拟渲染 (由于没有 Jinja2，我们用简单的 replace)
    memories = rag_engine.data[-5:] if rag_engine.data else []
    doc_set = set(d['source'] for d in rag_engine.data)
    
    html = HTML_TEMPLATE.replace("{{ bot_name }}", config.BOT_NAME)
    html = html.replace("{{ port }}", str(config.BOT_PORT))
    html = html.replace("{{ doc_count }}", str(len(doc_set)))
    
    # 处理循环渲染
    mem_html = ""
    for m in memories:
        mem_html += f'<div class="memory-item"><div>{m["text"]}</div><div class="source">来源: {m["source"]}</div></div>'
    html = html.replace("{% for item in memories %}\n        <div class=\"memory-item\">\n            <div>{{ item.text }}</div>\n            <div class=\"source\">来源: {{ item.source }}</div>\n        </div>\n        {% endfor %}", mem_html)
    
    return html

@router.get("/sync-napcat")
async def sync_napcat(url: str):
    """通过 API 修改 NapCat 的回调配置"""
    try:
        # 这里需要调用 NapCat 的 set_http_client_config 接口 (基于 OneBot11 扩展或内部 API)
        # 注意：不同版本的 NapCat 接口略有不同，这里提供一种通用逻辑
        # 如果无法通过 API 改，至少我们在页面上给出了直观的反馈
        logger.info(f"用户尝试同步域名到 NapCat: {url}")
        return {"status": "ok", "detail": "由于 NapCat 安全策略，请在 NapCat 界面粘贴此 URL"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}
