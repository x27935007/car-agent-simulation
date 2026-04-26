import os
import sys

if __name__ == "__main__":
    print("正在启动购车用户仿真系统...")
    
    # 确保当前目录在 sys.path 中
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    # 运行服务器
    from server import run_server
    run_server()
