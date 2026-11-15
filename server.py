# main.py
import os
import sys
import json
import asyncio
import traceback
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import uvicorn

# ─── SAFE IMPORT FOR RAILWAY DEBUGGING ───
try:
    import gen
except Exception as e:
    print("\n" + "="*50, file=sys.stderr)
    print("CRITICAL ERROR: Could not import gen.py", file=sys.stderr)
    print("="*50, file=sys.stderr)
    traceback.print_exc(file=sys.stderr)
    sys.stderr.flush()
    raise e

app = FastAPI()

class ConnectionManager:
    def __init__(self):
        self.active_connections = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
    
    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try: 
                await connection.send_text(message)
            except: 
                pass

manager = ConnectionManager()

# ─── HOOK INTO GEN.PY RICH CONSOLE ───
def make_logger(level):
    def logger(msg, *args, **kwargs):
        try: 
            loop = asyncio.get_running_loop()
            loop.create_task(manager.broadcast(json.dumps({"level": level, "message": str(msg)})))
        except: 
            pass
    return logger

gen.print_success = make_logger("success")
gen.print_error = make_logger("error")
gen.print_warning = make_logger("warning")
gen.print_info = make_logger("info")
gen.print_rare = make_logger("rare")

def web_registration_status(count, total, name, uid, password, account_id, region, is_ghost=False):
    msg = f"[{count}/{total}] Success | Name: {name} | UID: {uid} | Region: {region}"
    make_logger("success")(msg)
gen.print_registration_status = web_registration_status

def web_rarity_found(account_data, rarity_type, reason, rarity_score):
    msg = f"RARE FOUND #{rarity_score} | Name: {account_data.get('name')} | ID: {account_data.get('account_id')}"
    make_logger("rare")(msg)
gen.print_rarity_found = web_rarity_found

def web_couples_found(account1, account2, reason):
    msg = f"COUPLE MATCH | {account1.get('name')} & {account2.get('name')} | {reason}"
    make_logger("info")(msg)
gen.print_couples_found = web_couples_found

def safe_start_live(total, region, is_ghost, summary=None):
    with gen._live_lock:
        gen._STATUS.update({'current': 0, 'total': total, 'rare': 0, 'couples': 0, 'region': region, 'is_ghost': is_ghost, 'threads_alive': 0, 'elapsed': 0.0, 'speed': 0.0, 'last_event': 'starting...'})
        if summary is not None:
            gen._SUMMARY.clear()
            gen._SUMMARY.update(summary)
        with gen._recent_lock:
            gen._recent_accounts.clear()
gen.start_live = safe_start_live
gen.stop_live = lambda: None
gen._live = None

is_running = False

# ─── API ENDPOINTS ───

@app.post("/api/start")
async def start_generation(data: dict):
    global is_running
    if is_running:
        return {"status": "error", "message": "Already running"}
    
    count = data.get("count", 10)
    region = data.get("region", "IND")
    prefix = data.get("prefix", "ZHD")
    threads = data.get("threads", 5)
    avatar = data.get("avatar", True)
    activate = data.get("activate", True)
    proxy = data.get("proxy")
    rarity = data.get("rarity", 8)
    
    is_ghost = (region == "GHOST")
    if is_ghost: region = "BR"
    
    gen.settings.AVATAR_CHANGE_ON_GENERATE = avatar
    gen.settings.ACTIVATE_ON_RUN = activate
    gen.settings.RARITY_SCORE_THRESHOLD = rarity
    gen.settings.SUCCESS_COUNTER = 0
    gen.settings.RARE_COUNTER = 0
    gen.settings.COUPLES_COUNTER = 0
    gen.settings.ACTIVATED_COUNTER = 0
    gen.settings.EXIT_FLAG = False
    gen.settings.TARGET_ACCOUNTS = count
    gen.settings.INFLIGHT_COUNTER = 0
    
    if proxy and proxy.strip():
        gen.PROXY_LIST = [proxy.strip()]
        gen.set_proxy_mode(True)
        make_logger("info")(f"Proxy enabled: {proxy}")
    else:
        gen.set_proxy_mode(False)
    
    async def run_gen():
        global is_running
        is_running = True
        try:
            gen.start_save_writer()
            gen.start_live(count, region, is_ghost)
            make_logger("success")(f"Starting generation: {count} accounts ({region})")
            
            tasks = [asyncio.create_task(gen.worker(region, prefix, prefix, count, i+1, is_ghost)) for i in range(threads)]
            
            while any(not t.done() for t in tasks):
                if gen.settings.EXIT_FLAG and not all(t.done() for t in tasks):
                    for t in tasks:
                        if not t.done(): 
                            t.cancel()
                await asyncio.sleep(0.5)
                
            gen.settings.EXIT_FLAG = True
            await asyncio.gather(*tasks, return_exceptions=True)
            gen.flush_saves()
            make_logger("success")("Generation complete.")
        except Exception as e:
            make_logger("error")(f"Error: {e}")
        finally:
            is_running = False
            
    asyncio.create_task(run_gen())
    return {"status": "ok"}

@app.post("/api/stop")
async def stop_generation():
    global is_running
    if not is_running:
        return {"status": "error", "message": "Not running"}
    gen.settings.EXIT_FLAG = True
    make_logger("warning")("Stop requested. Finishing current tasks...")
    return {"status": "ok"}

@app.get("/api/stats")
async def get_stats():
    return {
        "success": gen.settings.SUCCESS_COUNTER,
        "rare": gen.settings.RARE_COUNTER,
        "couples": gen.settings.COUPLES_COUNTER,
        "activated": getattr(gen.settings, 'ACTIVATED_COUNTER', 0),
        "target": gen.settings.TARGET_ACCOUNTS,
        "is_running": is_running
    }

# ─── DATA VAULT API ───

@app.get("/api/files")
async def get_files():
    files = []
    folders = {
        "ACCOUNTS": gen.settings.ACCOUNTS_FOLDER,
        "TOKENS": gen.settings.TOKENS_FOLDER,
        "RARE": gen.settings.RARE_ACCOUNTS_FOLDER,
        "COUPLES": gen.settings.COUPLES_ACCOUNTS_FOLDER,
        "GHOST": gen.settings.GHOST_ACCOUNTS_FOLDER
    }
    for label, path in folders.items():
        if os.path.exists(path):
            for f in os.listdir(path):
                if f.endswith('.json'):
                    files.append({"label": f"[{label}] {f}", "path": os.path.join(path, f)})
    files.sort(key=lambda x: x["label"])
    return {"files": files}

@app.get("/api/file_data")
async def get_file_data(path: str):
    abs_path = os.path.abspath(path)
    base_path = os.path.abspath(gen.settings.BASE_FOLDER)
    if not abs_path.startswith(base_path):
        return {"status": "error", "message": "Access Denied"}
        
    try:
        with open(abs_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return {"status": "ok", "data": data}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# ─── WEBSOCKET & ROOT ───

@app.websocket("/ws/logs")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True: 
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/")
async def get_dashboard():
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        return HTMLResponse(content="<h1>index.html not found</h1>")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    print(f"\n🚀 Web Dashboard running on http://localhost:{port}\n")
    uvicorn.run(app, host="0.0.0.0", port=port)
