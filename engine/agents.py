import random

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
