# 购车用户仿真 Agent 系统 (Car-Agent-Simulation)

基于信息熵稳定态自动停止的万人级市场仿真系统，支持 KOL 引导、谣言传播、竞品攻击，并能实时输出结构化的商业决策报告。

## 🌟 核心特性

- **万人级 Agent 模拟**：实时模拟 10,000 名具备不同属性（价格、续航、智驾、安全敏感度）的用户。
- **KOL 影响模型**：20 名不同类型的 KOL（专家、媒体、炒作、中立）基于用户需求匹配度产生差异化影响。
- **竞品博弈**：内置竞品 Agent，模拟真实市场中的负面攻击与舆论干扰。
- **实时可视化看板**：基于 Chart.js 的动态趋势图，直观展示系统熵值（Entropy）与观点分布演变。
- **智能停止机制**：基于信息熵的稳定性检测，当舆论达到动态平衡时自动停止并生成报告。

## 🚀 快速启动

### 1. 克隆仓库
```bash
git clone https://github.com/你的用户名/car-agent-simulation.git
cd car-agent-simulation
```

### 2. 运行服务器
无需安装额外依赖（仅需 Python 3.7+ 标准库）：
```bash
python main.py
```

### 3. 访问看板
在浏览器中打开：
[http://localhost:8003/index.html](http://localhost:8003/index.html)

## ⚙️ 配置说明

你可以通过修改根目录下的 `config.py` 来调整仿真参数：
- `AGENT_COUNT`: 模拟的用户总数。
- `KOL_COUNT`: KOL 的数量。
- `ENTROPY_STOP_THRESHOLD`: 熵稳定判定的阈值。
- `PORT`: Web 服务的端口号。

## 📂 项目结构

```text
├── main.py               # 🚀 系统主入口
├── server.py             # Web 服务（提供 API + 页面）
├── config.py             # 商业化配置
├── requirements.txt      # 依赖清单
├── .gitignore            # Git 忽略配置
├── engine/               # 核心仿真引擎目录
│   ├── agents.py         # 用户/KOL/竞品 Agent 定义
│   ├── entropy.py        # 熵计算 + 稳定停止核心
│   └── simulator.py      # 模拟调度引擎
└── web/                  # 前端看板目录
    ├── index.html        # 看板页面
    ├── app.js            # 前端逻辑
    └── style.css         # 界面样式
```

## 📊 仿真逻辑说明

1. **初始化**：创建 10,000 名用户，其初始观点（正向/负向/中立）随机分配。
2. **影响循环**：
   - KOL 发布消息，如果消息触达用户的核心需求点，影响力将获得加成。
   - 竞品 Agent 随机发动负面攻击，试图扭转用户观点。
3. **熵值计算**：每一步计算全系统的观点熵值，反映舆论的混乱/极化程度。
4. **稳定判定**：当连续数步熵值波动小于阈值时，判定市场达到“认知闭环”，停止模拟并生成洞察。

## 📝 许可证

MIT License
