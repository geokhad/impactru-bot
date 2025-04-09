import datetime

USAGE_FILE = "gpt_usage.txt"
LIMIT_PER_DAY = 5

def check_and_increment_usage(user_id):
    today = datetime.date.today().isoformat()
    records = {}

    # Читаем файл
    try:
        with open(USAGE_FILE, "r", encoding="utf-8") as f:
            for line in f:
                uid, date_str, count = line.strip().split(",")
                records[(uid, date_str)] = int(count)
    except FileNotFoundError:
        pass

    key = (str(user_id), today)
    count = records.get(key, 0)

    if count >= LIMIT_PER_DAY:
        return False, LIMIT_PER_DAY

    # Обновляем счётчик
    records[key] = count + 1

    # Записываем обратно
    with open(USAGE_FILE, "w", encoding="utf-8") as f:
        for (uid, date), cnt in records.items():
            f.write(f"{uid},{date},{cnt}\n")

    return True, LIMIT_PER_DAY - (count + 1)

