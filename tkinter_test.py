from tkinter import *
from onkyo_controller import *

root = Tk()

root.title("welcoem to app")
root.geometry('1000x500')

l1 = Label(root, text='Control your Onkyo from here!')
l1.grid(column=1, row=0)

power_stat = query_onkyo('PWRQSTN', expected_prefix='!1PWR', verbose=False).split('!1PWR')[1][:2]
l2 = Label(root, text='Receiver: On' if power_stat == '01' else 'Receiver: Standby')
l2.grid(column=0, row=1)

def clicked_pwr_toggle():
    pwr_status = query_onkyo(
        'PWRQSTN', expected_prefix='!1PWR', verbose=False
    ).split('!1PWR')[1][:2]
    send_command('PWR00' if pwr_status == '01' else 'PWR01')
    l2.configure(text='Receiver: On' if pwr_status == '00' else 'Receiver: Standby')

b1 = Button(root, text='Toggle Power',
             fg='red', command=clicked_pwr_toggle)

b1.grid(column=1, row=1)

# v2 = DoubleVar()

# def show2():
#     sel = 'Vertical Scale Value = ' + str(v2.get())
#     l3.config(text=sel, font=('Courier', 14))

# s2 = Scale(
#     root,
#     variable=v2,
#     from_=100,
#     to=0,
#     orient=VERTICAL,
# )

# l4 = Label(root, text='Vertical Scaler')
# b2 = Button(root, text='Display Vertical',
#             command=show2,
#             bg='purple',
#             fg='white')

# l3 = Label(root)
# l3.grid()

# s2.pack(anchor=CENTER)
# l4.pack()
# b2.pack()
# l2.pack()

root.mainloop()