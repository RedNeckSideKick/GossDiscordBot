import os
import gspread

print("Imports complete, authenticating")
filedir = os.path.dirname(os.path.abspath(__file__))
gc = gspread.service_account(filename=os.path.join(filedir, "service_account.json"))

print("Authentication complete, opening spreadsheet")
sh = gc.open("Goss-Scholars-21")

print(sh.sheet1.get('A1:J10'))