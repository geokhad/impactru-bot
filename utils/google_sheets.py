import gspread
import json
import os
from oauth2client.service_account import ServiceAccountCredentials

def save_feedback_to_google_sheets(name, user_id, message):
    # Загружаем JSON-ключ из переменной окружения
    credentials_json = json.loads(os.environ["GOOGLE_APPLICATION_CREDENTIALS_JSON"])
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_json, scope)
    client = gspread.authorize(creds)
    sheet = client.open("ImpactRU Feedback").sheet1
    sheet.append_row([name, user_id, message])

