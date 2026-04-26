import time
import random
import math
from collections import Counter

AGENT_COUNT = 10000
KOL_COUNT = 20
SIMULATION_STEP_SECONDS = 0.1
ENTROPY_STOP_THRESHOLD = 0.002
CONSECUTIVE_STABLE_STEPS = 5

class UserAgent:
    def __init__(self):
        self.opinion = random.choice(["positive", "negative", "neutral"])
        self.needs = {
            "price": random.uniform(8, 25),
            "range": random.uniform(300, 800),
            "smart": random.uniform(0, 1),
            "safety": random.uniform(0, 1)
        }
        self.trust = random.uniform(0.1, 0.9)
        self.follow_rate = random.uniform(0.05, 0.4)

class KOLAgent:
    def __init__(self, id):
        self.id = id
        self.influence = random.uniform(0.4, 0.95)
        self.type = random.choice(["expert", "media", "hype", "neutral"])
        self.message = random.choice([
            "续航很重要",
            "智驾是未来",
            "安全不能妥协",
            "竞品有隐患",
            "价格决定销量"
        ])
        self.is_attack_competitor = random.random() < 0.3

class CompetitorAgent:
    def __init__(self):
        self.mode = random.choice(["normal", "attack"])
        self.attack_msg = random.choice([
            "刹车问题",
            "续航虚标",
            "智驾失灵",
            "做工差"
        ])

def calculate_entropy(prob_list):
    entropy = 0.0
    for p in prob_list:
        if p > 0:
            entropy -= p * math.log2(p)
    return entropy

def get_system_entropy(users):
    opinions = [u.opinion for u in users]
    cnt = Counter(opinions)
    total = len(opinions)
    probs = [v/total for v in cnt.values()]
    return calculate_entropy(probs), cnt

class SimulationEngine:
    def __init__(self):
        self.users = [UserAgent() for _ in range(AGENT_COUNT)]
        self.kols = [KOLAgent(i) for i in range(KOL_COUNT)]
        self.competitor = CompetitorAgent()
        self.step = 0
        self.last_entropy = None
        self.stable_count = 0
        self.is_running = False
        self.history = []
        self.current_counts = {}
        self.current_entropy = 0
        self.final_report = None

    def run_step(self):
        self.step += 1
        # 1. KOL 影响
        for kol in self.kols:
            message_map = {
                "续航很重要": "range",
                "智驾是未来": "smart",
                "安全不能妥协": "safety",
                "价格决定销量": "price",
                "竞品有隐患": "safety"
            }
            target_need = message_map.get(kol.message)
            target_users = random.sample(self.users, int(len(self.users)*0.05))
            for u in target_users:
                effective_influence = kol.influence
                if target_need:
                    need_value = u.needs.get(target_need, 0.5)
                    if target_need == "range":
                        need_value = (need_value - 300) / 500
                    elif target_need == "price":
                        need_value = (25 - need_value) / 17
                    effective_influence *= (1 + need_value)

                if random.random() < u.trust * effective_influence:
                    if kol.is_attack_competitor:
                         u.opinion = "negative"
                    else:
                         u.opinion = "positive" if kol.type != "hype" else "negative"

        # 2. 竞品攻击
        if self.competitor.mode == "attack":
            targets = random.sample(self.users, int(len(self.users)*0.05))
            for u in targets:
                u.opinion = "negative"

        self.current_entropy, self.current_counts = get_system_entropy(self.users)
        self.history.append(self.current_entropy)

        is_stable = False
        if len(self.history) >= CONSECUTIVE_STABLE_STEPS:
            window = self.history[-CONSECUTIVE_STABLE_STEPS:]
            diff = max(window) - min(window)
            if diff < ENTROPY_STOP_THRESHOLD:
                is_stable = True
                print(f"Engine: Stability reached (diff={diff:.6f}). Generating report...", flush=True)
                self.generate_report()

        return is_stable

    def generate_report(self):
        # 简单模拟报告生成逻辑，参考文档
        report = {
            "must_have": ["续航", "安全", "价格"],
            "risk": ["智驾谣言", "竞品攻击(" + self.competitor.attack_msg + ")"],
            "kol_best": [k.type for k in self.kols if k.influence > 0.8][:2],
            "competitor_status": self.competitor.mode
        }
        # 确保 kol_best 不为空
        if not report["kol_best"]:
            report["kol_best"] = ["expert", "media"]
            
        self.final_report = report
        print(f"Engine: Report generated: {self.final_report}", flush=True)

    def get_status(self):
        return {
            "step": self.step,
            "entropy": self.current_entropy,
            "counts": dict(self.current_counts),
            "is_stable": self.final_report is not None,
            "history_length": len(self.history),
            "report": self.final_report
        }

def run_simulation():
    print("系统启动 → 创建10000用户 + 20 KOL + 谣言/竞品攻击", flush=True)
    engine = SimulationEngine()
    
    while True:
        is_stable = engine.run_step()
        status = engine.get_status()
        print(f"Step {status['step']} | Entropy: {status['entropy']:.4f} | Opinions: {status['counts']}", flush=True)

        if is_stable:
            print(f"DONE: Entropy stabilized (diff < {ENTROPY_STOP_THRESHOLD} for {CONSECUTIVE_STABLE_STEPS} steps)", flush=True)
            break
        time.sleep(SIMULATION_STEP_SECONDS)

    return engine.get_status()

if __name__ == "__main__":
    result = run_simulation()