from flask import Flask, jsonify, send_from_directory, request, Response
import threading
import os
import datetime
from engine.simulator import SimulationEngine
from config import PORT, SIMULATION_STEP_SECONDS
from user_db import check_user, get_balance, cost, recharge
from history import add_record, get_history
from export_pdf import gen_pdf

app = Flask(__name__)

# 全局仿真状态
engine = None
simulation_thread = None
stop_event = threading.Event()
current_simulation_info = {}

# 静态文件目录
WEB_DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'web')

@app.route("/")
def index():
    return send_from_directory(WEB_DIRECTORY, "home.html")

@app.route("/login")
def login_page():
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
    global engine, simulation_thread, stop_event, current_simulation_info
    d = request.json
    user = d.get("user")
    pwd = d.get("pwd")
    model_id = d.get("model_id", "1")
    
    if not check_user(user, pwd):
        return jsonify(ok=0, msg="登录失败")
    if not cost(user, 1):
        return jsonify(ok=0, msg="余额不足")
    
    if simulation_thread and simulation_thread.is_alive():
        return jsonify(ok=0, msg="仿真已在运行中")

    # 获取车型名称
    models = {
        "1": "紧凑型家用SUV",
        "2": "中型智能电动SUV",
        "3": "高端豪华电动轿车"
    }
    model_name = models.get(str(model_id), "未知车型")

    engine = SimulationEngine()
    current_simulation_info = {
        "user": user,
        "model_name": model_name,
        "start_time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    stop_event.clear()
    simulation_thread = threading.Thread(target=run_simulation_loop)
    simulation_thread.daemon = True
    simulation_thread.start()
    
    return jsonify(ok=1, status="started", balance=get_balance(user))

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

@app.route("/api/history")
def history_api():
    return jsonify(history=get_history())

@app.route("/api/download")
def download():
    if engine:
        status = engine.get_status()
        report = status.get("report")
        if report:
            # 补全报告信息用于打印
            report['time'] = current_simulation_info.get("start_time")
            report['model_name'] = current_simulation_info.get("model_name")
            data = gen_pdf(report)
            return Response(data, mimetype="text/plain", 
                          headers={"Content-Disposition": f"attachment;filename=report_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"})
    return jsonify(ok=0, msg="暂无可用报告，请先完成仿真")

@app.route("/api/admin/recharge", methods=["POST"])
def admin_recharge():
    d = request.json
    if d.get("admin_pwd") != "admin888":
        return jsonify(ok=0, msg="管理员权限验证失败")
    if recharge(d.get("user"), d.get("money", 0)):
        return jsonify(ok=1, balance=get_balance(d.get("user")))
    return jsonify(ok=0)

def run_simulation_loop():
    print("Simulation background thread started")
    while not stop_event.is_set():
        is_stable = engine.run_step()
        if is_stable:
            print("Simulation reached stability naturally")
            # 记录到历史
            status = engine.get_status()
            add_record(current_simulation_info["user"], current_simulation_info["model_name"], status["report"])
            break
        import time
        time.sleep(SIMULATION_STEP_SECONDS)
    print("Simulation background thread stopped")

def run_server():
    app.run(host="0.0.0.0", port=PORT, debug=False)

if __name__ == "__main__":
    run_server()
