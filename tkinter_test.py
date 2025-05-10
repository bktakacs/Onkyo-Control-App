from tkinter import *
from onkyo_controller import *

root = Tk()

root.title("welcoem to app")
root.geometry('1000x500')

lbl = Label(root, text='Control your Onkyo from here!')
lbl.grid()

# txt = Entry(root, width=10)
# txt.grid(column=1, row=0)


def clicked_pwr_toggle():
    pwr_status = get_power_status(receiver_ip=receiver_ip)
    
    send_command(receiver_ip, receiver_port, "PWR01")
    lbl.configure(text='Receiver off')

btn = Button(root, text='Click here to power on your receiver',
             fg='red', command=clicked_pwr_toggle)

btn.grid(column=2, row=0)




root.mainloop()