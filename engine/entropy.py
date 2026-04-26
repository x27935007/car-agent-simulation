import math
from collections import Counter

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

def is_stable(history, threshold=0.002, steps=5):
    if len(history) < steps:
        return False
    window = history[-steps:]
    return max(window) - min(window) < threshold
