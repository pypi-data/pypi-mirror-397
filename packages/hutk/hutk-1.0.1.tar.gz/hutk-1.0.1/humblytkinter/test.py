from __init__ import *

app = MyGUI("Test Window")

app.make_label("سلام دنیا", label_number=0, fg="blue", bg="yellow")
app.make_button("بستن", button_number=1, button_command=app.root.destroy, fg="white", bg="red")
entry = app.make_entry(entry_number=2, fg="green", bg="lightgray")

app.run()