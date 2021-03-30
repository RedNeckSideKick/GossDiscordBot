import pygsheets
import numpy as np

print("Authorizing...")
gc = pygsheets.authorize()
print("Auth complete")

# Open spreadsheet and then worksheet
print("Opening sheet...")
sh = gc.open('Test Spreadsheet')
print("Sheet opened")
wks = sh.sheet1

# model_cell = pygsheets.Cell("A1")

# model_cell.set_number_format(
#     format_type = pygsheets.FormatType.PERCENT,
#     pattern = "0%"
# )
# # first apply the percentage formatting
# pygsheets.DataRange(
#     'A1' , 'J10' , worksheet = wks
#  ).apply_format(model_cell)

# # now apply the row-colouring interchangeably
# gray_cell = pygsheets.Cell("A1")
# gray_cell.color = (0.9529412, 0.9529412, 0.9529412, 0)

# white_cell = pygsheets.Cell("A2")
# white_cell.color = (1, 1, 1, 0)

# cells = [gray_cell, white_cell]

# for r in range(1, 10 + 1):
#     print(f"Doing row {r} ...", flush = True, end = "\r")
#     wks.get_row(r, returnas = "range").apply_format(cells[ r % 2 ], fields = "userEnteredFormat.backgroundColor")

cells = wks.find('Ethan Kessel')
for cell in cells:
    cell.color = (1, 0, 0, 0)
    wks.range(f"{cell.label}:{cell.label}", returnas='range').apply_format(cell, fields = "userEnteredFormat.backgroundColor")
print(cells)

# Update a cell with value (just to let him know values is updated ;) )
wks.update_value('A1', "Hey yank this numpy array")
my_nparray = np.random.randint(10, size=(3, 4))

# update the sheet with array
wks.update_values('A2', my_nparray.tolist())

# share the sheet with your friend
# sh.share("thespacekobold@gmail.com")