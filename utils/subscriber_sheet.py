import gspread
import json
import os
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

def save_subscriber_to_sheet(user_id, full_name, username):
    credentials_json = json.loads(os.environ["GOOGLE_APPLICATION_CREDENTIALS_JSON"])
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_json, scope)
    client = gspread.authorize(creds)

    sheet = client.open("ImpactRU Subscribers").sheet1
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    sheet.append_row([str(user_id), full_name, username or "", now])

