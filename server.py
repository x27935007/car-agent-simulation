import http.server
import socketserver
import json
import threading
import time
import os
from urllib.parse import urlparse
from engine.simulator import SimulationEngine
from config import PORT, SIMULATION_STEP_SECONDS

# 静态文件目录
WEB_DIRECTORY = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'web')

# 全局仿真引擎实例
engine = None
simulation_thread = None
stop_event = threading.Event()

class SimulationHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=WEB_DIRECTORY, **kwargs)

    def do_GET(self):
        global engine, simulation_thread, stop_event
        parsed_path = urlparse(self.path).path
        
        if parsed_path == '/':
            self.path = '/index.html'
            return super().do_GET()

        if parsed_path == '/api/status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Expires', '0')
            self.end_headers()
            if engine:
                status = engine.get_status()
                status['running'] = not stop_event.is_set() and simulation_thread is not None and simulation_thread.is_alive()
            else:
                status = {'running': False, 'step': 0, 'entropy': 0, 'counts': {}}
            self.wfile.write(json.dumps(status).encode())
        
        elif parsed_path == '/api/start':
            if simulation_thread and simulation_thread.is_alive():
                self.send_response(400)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Simulation already running'}).encode())
                return

            engine = SimulationEngine()
            stop_event.clear()
            simulation_thread = threading.Thread(target=self.run_simulation_loop)
            simulation_thread.daemon = True
            simulation_thread.start()
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'started'}).encode())

        elif parsed_path == '/api/stop':
            stop_event.set()
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'stopping'}).encode())
        
        else:
            return super().do_GET()

    def run_simulation_loop(self):
        print("Simulation background thread started")
        while not stop_event.is_set():
            is_stable = engine.run_step()
            if is_stable:
                print("Simulation reached stability naturally")
                break
            time.sleep(SIMULATION_STEP_SECONDS)
        print("Simulation background thread stopped")

def run_server():
    # 确保在正确的目录下运行以提供静态文件
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    # 设置端口复用，避免频繁重启时的 Address already in use 错误
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), SimulationHandler) as httpd:
        print(f"Serving at http://localhost:{PORT}")
        print(f"Web Directory: {WEB_DIRECTORY}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server...")
            httpd.shutdown()

if __name__ == "__main__":
    run_server()
