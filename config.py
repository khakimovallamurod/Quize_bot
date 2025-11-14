from dotenv import load_dotenv
import os
import ast

load_dotenv()
def get_token():
    TOKEN = os.getenv("TOKEN")
    if TOKEN is None:
        raise ValueError("TOKEN not found.")
    return TOKEN

load_dotenv()
def get_adminid():
    admin_id_raw = os.getenv("admin_id")
    if admin_id_raw is None:
        raise ValueError("admin_id not found.")

    admin_id_list = ast.literal_eval(admin_id_raw)

    return admin_id_list
