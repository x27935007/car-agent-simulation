users = {
    "admin": {"pwd": "admin888", "balance": 9999, "role": "admin"}
}

def check_user(user, pwd):
    return users.get(user, {}).get("pwd") == pwd

def get_balance(user):
    return users.get(user, {}).get("balance", 0)

def cost(user, num=1):
    if users.get(user, {}).get("balance", 0) >= num:
        users[user]["balance"] -= num
        return True
    return False

def recharge(user, money):
    if user not in users:
        users[user] = {"pwd": "123456", "balance": 0, "role": "user"}
    users[user]["balance"] += money
    return True
