from collections import defaultdict

# Хранилище истории в оперативной памяти
user_dialogs = defaultdict(list)

def add_to_dialog(user_id, role, message):
    user_dialogs[user_id].append({"role": role, "content": message})
    # Обрезаем историю до 10 сообщений максимум
    if len(user_dialogs[user_id]) > 10:
        user_dialogs[user_id] = user_dialogs[user_id][-10:]

def get_dialog(user_id):
    return user_dialogs[user_id]

def reset_dialog(user_id):
    user_dialogs[user_id] = []

