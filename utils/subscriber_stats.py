import gspread
import json
import os
from oauth2client.service_account import ServiceAccountCredentials

def get_subscriber_count():
    credentials_json = json.loads(os.environ["GOOGLE_APPLICATION_CREDENTIALS_JSON"])
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(credentials_json, scope)
    client = gspread.authorize(creds)

    sheet = client.open("ImpactRU Subscribers").sheet1
    records = sheet.get_all_records()

    unique_ids = set(str(row["ID"]) for row in records if row.get("ID"))
    return len(unique_ids)


