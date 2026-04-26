from flask import Flask, jsonify, send_from_directory, request
import threading
import os
from engine.simulator import SimulationEngine
from config import PORT, SIMULATION_STEP_SECONDS
from user_db import check_user, get_balance, cost

app = Flask(__name__)

# 全局仿真引擎实例
engine = None
simulation_thread = None
stop_event = threading.Event()

# 静态文件目录
WEB_DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'web')

@app.route("/")
def index():
    return send_from_directory(WEB_DIRECTORY, "login.html")

@app.route("/web/<path:p>")
def static_web(p):
    return send_from_directory(WEB_DIRECTORY, p)

@app.route("/api/login", methods=["POST"])
def login():
    d = request.json
    if check_user(d.get("user"), d.get("pwd")):
        return jsonify(ok=1, balance=get_balance(d["user"]))
    return jsonify(ok=0)

@app.route("/api/start", methods=["POST"])
def start():
    global engine, simulation_thread, stop_event
    d = request.json
    if not check_user(d.get("user"), d.get("pwd")):
        return jsonify(ok=0, msg="登录失败")
    if not cost(d["user"], 1):
        return jsonify(ok=0, msg="余额不足")
    
    if simulation_thread and simulation_thread.is_alive():
        return jsonify(ok=0, msg="仿真已在运行中")

    engine = SimulationEngine()
    stop_event.clear()
    simulation_thread = threading.Thread(target=run_simulation_loop)
    simulation_thread.daemon = True
    simulation_thread.start()
    
    return jsonify(ok=1, status="started", balance=get_balance(d["user"]))

@app.route("/api/status")
def status():
    if engine:
        status_data = engine.get_status()
        status_data['running'] = not stop_event.is_set() and simulation_thread is not None and simulation_thread.is_alive()
        return jsonify(status_data)
    return jsonify({'running': False, 'step': 0, 'entropy': 0, 'counts': {}})

@app.route("/api/stop", methods=["POST"])
def stop():
    global stop_event
    stop_event.set()
    return jsonify(ok=1, status="stopping")

@app.route("/api/car_models")
def car_models():
    return jsonify(models=[
        {"id": 1, "name": "紧凑型家用SUV"},
        {"id": 2, "name": "中型智能电动SUV"},
        {"id": 3, "name": "高端豪华电动轿车"}
    ])

def run_simulation_loop():
    print("Simulation background thread started")
    while not stop_event.is_set():
        is_stable = engine.run_step()
        if is_stable:
            print("Simulation reached stability naturally")
            break
        import time
        time.sleep(SIMULATION_STEP_SECONDS)
    print("Simulation background thread stopped")

def run_server():
    app.run(host="0.0.0.0", port=PORT, debug=False)

if __name__ == "__main__":
    run_server()
