import os
import sys

# 将 agents 目录添加到路径中
sys.path.append(os.path.join(os.path.dirname(__file__), 'agents'))

if __name__ == "__main__":
    print("正在启动购车用户仿真系统...")
    # 切换工作目录到 agents 文件夹以确保静态文件能被 server.py 正确找到
    os.chdir(os.path.join(os.path.dirname(__file__), 'agents'))
    
    # 运行服务器
    from server import run_server
    run_server()
