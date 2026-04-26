history_list = []

def add_record(user, model_name, result):
    import datetime
    history_list.append({
        "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user": user,
        "model": model_name,
        "result": result
    })

def get_history():
    return history_list
