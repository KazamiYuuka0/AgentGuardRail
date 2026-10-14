from flask import Flask, render_template_string, request, jsonify
from Register import Register

app = Flask(__name__)
register = Register()

HTML = r"""
<!DOCTYPE html>
<html lang="zh">
<head>
<meta charset="UTF-8">
<title>AI GuardRail Demo</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: -apple-system, sans-serif; background: #f0f2f5; height: 100vh; display: flex; flex-direction: column; }
  header { background: #1a1a2e; color: #fff; padding: 14px 24px; text-align: center; font-size: 20px; }
  .container { display: flex; flex: 1; overflow: hidden; }
  .panel { flex: 1; display: flex; flex-direction: column; border-right: 1px solid #ddd; }
  .panel:last-child { border-right: none; }
  .panel-header { padding: 10px 16px; font-weight: bold; font-size: 15px; }
  .panel-header.safe { background: #d4edda; color: #155724; }
  .panel-header.unsafe { background: #f8d7da; color: #721c24; }
  .messages { flex: 1; overflow-y: auto; padding: 16px; display: flex; flex-direction: column; gap: 10px; }
  .msg { max-width: 80%%; padding: 10px 14px; border-radius: 16px; line-height: 1.5; font-size: 14px; word-break: break-word; white-space: pre-wrap; }
  .msg.user { align-self: flex-end; background: #007bff; color: #fff; border-bottom-right-radius: 4px; }
  .msg.bot { align-self: flex-start; background: #fff; color: #333; border-bottom-left-radius: 4px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
  .input-bar { display: flex; padding: 12px; gap: 8px; background: #fff; border-top: 1px solid #ddd; }
  .input-bar input { flex: 1; padding: 10px 14px; border: 1px solid #ccc; border-radius: 20px; outline: none; font-size: 14px; }
  .input-bar button { padding: 8px 20px; border: none; border-radius: 20px; cursor: pointer; font-size: 14px; color: #fff; }
  .btn-safe { background: #28a745; }
  .btn-unsafe { background: #dc3545; }
  .btn-reset { background: #6c757d; font-size: 12px; padding: 6px 12px; }
  .toolbar { display: flex; gap: 6px; padding: 6px 12px; background: #fafafa; border-top: 1px solid #eee; }
  .loading { opacity: 0.6; font-style: italic; }
</style>
</head>
<body>
<header>AI 安全护栏对比演示</header>
<div class="container">
  <div class="panel">
    <div class="panel-header safe">有护栏 (Safe)</div>
    <div class="messages" id="msgs-safe"></div>
    <div class="toolbar">
      <button class="btn-reset" onclick="resetChat('safe')">清空会话</button>
    </div>
    <div class="input-bar">
      <input id="input-safe" placeholder="输入消息..." onkeydown="if(event.key==='Enter')send('safe')">
      <button class="btn-safe" onclick="send('safe')">发送</button>
    </div>
  </div>
  <div class="panel">
    <div class="panel-header unsafe">无护栏 (Unsafe)</div>
    <div class="messages" id="msgs-unsafe"></div>
    <div class="toolbar">
      <button class="btn-reset" onclick="resetChat('unsafe')">清空会话</button>
    </div>
    <div class="input-bar">
      <input id="input-unsafe" placeholder="输入消息..." onkeydown="if(event.key==='Enter')send('unsafe')">
      <button class="btn-unsafe" onclick="send('unsafe')">发送</button>
    </div>
  </div>
</div>
<script>
async function send(mode) {
  const input = document.getElementById('input-' + mode);
  const text = input.value.trim();
  if (!text) return;
  input.value = '';
  input.disabled = true;

  addMsg(mode, 'user', text);
  const loadingEl = addMsg(mode, 'bot', '思考中...', true);

  try {
    const res = await fetch('/chat/' + mode, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({message: text})
    });
    const data = await res.json();
    loadingEl.classList.remove('loading');
    loadingEl.textContent = data.reply;
  } catch(e) {
    loadingEl.classList.remove('loading');
    loadingEl.textContent = '请求失败: ' + e.message;
  }
  input.disabled = false;
  input.focus();
}

function addMsg(mode, role, text, loading) {
  const container = document.getElementById('msgs-' + mode);
  const div = document.createElement('div');
  div.className = 'msg ' + role + (loading ? ' loading' : '');
  div.textContent = text;
  container.appendChild(div);
  container.scrollTop = container.scrollHeight;
  return div;
}

async function resetChat(mode) {
  await fetch('/reset/' + mode, {method: 'POST'});
  document.getElementById('msgs-' + mode).innerHTML = '';
}
</script>
</body>
</html>
"""


@app.route("/")
def index():
    return render_template_string(HTML)


@app.route("/chat/<mode>", methods=["POST"])
def chat(mode):
    data = request.get_json()
    message = data.get("message", "")
    if mode == "safe":
        reply = register.agent.chat(message)
    else:
        reply = register.agent_unsafe.chat(message)
    return jsonify({"reply": reply})


@app.route("/reset/<mode>", methods=["POST"])
def reset(mode):
    if mode == "safe":
        register.agent.reset()
    else:
        register.agent_unsafe.reset()
    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
