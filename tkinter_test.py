from tkinter import *
from onkyo_controller import *

################################################################################
# DEFINE FUNCTIONS
def periodic_query():
    global current_power_status
    current_power_status = query_onkyo('PWRQTSN', expected_prefix='!1PWR', verbose=True)#.split('!PWR')[1][:2]
    global current_selected_input
    current_selected_input = query_onkyo('SLIQSTN', expected_prefix='!1SLI', verbose=True)#.split('!SLI')[1][:2]

    root.after(600000, periodic_query)

################################################################################
# MAIN LOOP

root = Tk()

root.title("welcoem to app")
root.geometry('1000x500')

# periodic_query()

################################################################################
# LABEL 1

l1 = Label(root, text='Control your Onkyo from here!')
l1.grid(column=1, row=0)

################################################################################
# LABEL 2 & BUTTON 1: POWER TOGGLE

get_power_status = query_onkyo('PWRQSTN', expected_prefix='!1PWR', verbose=False).split('!1PWR')[1][:2]
l2 = Label(root, text='Receiver: On' if get_power_status == '01' else 'Receiver: Standby')
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

################################################################################
# LABEL 3 & SCALE 1: VOLUME SLIDER

l3 = Label(root,
           text='Volume Slider')
l3.grid(column=0, row=2)

# query volume and set as current
get_current_volume = query_onkyo('MVLQSTN', expected_prefix='!1MVL', verbose=False).split('!1MVL')[1][:2]
current_volume = DoubleVar()
current_volume.set(int(get_current_volume, 16)) # convert hex to decimal

def slider_changed(event):
    send_command("MVL" + str(db_to_hex(slider.get() / 2)))
    # print('Volume changed to', slider.get())

slider = Scale(
    root,
    from_=0,
    to=60,
    orient='horizontal',  # horizontal
    variable=current_volume,
    command=slider_changed
)

slider.grid(column=1, row=2)

################################################################################
# LABEL 4 & BUTTON 2: TOGGLE MUTE

# get mute status
get_mute_status = query_onkyo('AMTQSTN', expected_prefix='!1AMT', verbose=False).split('!1AMT')[1][:2]
# display mute status
l4 = Label(root,
           text='Mute: On' if get_mute_status == '01' else 'Mute: Off')
l4.grid(column=0, row=3)

# mute toggle event
def clicked_mute_toggle():
    temp_mute_status = query_onkyo(
        'AMTQSTN', expected_prefix='!1AMT', verbose=False
    ).split('!1AMT')[1][:2]
    send_command('AMT00' if temp_mute_status == '01' else 'AMT01')
    l4.configure(text='Mute: On' if temp_mute_status == '00' else 'Mute: Off')

# mute toggle button
b2 = Button(root,
            text='Toggle Mute',
            fg='Red',
            command=clicked_mute_toggle)

b2.grid(column=1, row=3)

################################################################################
# LABEL 5 & RADIOBUTTON INPUT SELECTOR

l5 = Label(root,
           text='Select Audio Input')
l5.grid(column=0, row=4)

def select_audio_input():
    selected = selected_input.get()
    send_command('SLI' + str(selected))

# set default input to PC
selected_input = StringVar()
selected_input.set('05')

# set radio buttons
r1 = Radiobutton(root,
                 text='mac Mini (PC)',
                 value='05',
                 variable=selected_input,
                 command=select_audio_input,)
r2 = Radiobutton(root,
                 text='Record Player (PHONO)',
                 value='22',
                 variable=selected_input,
                 command=select_audio_input,)

r1.grid(column=1, row=4)
r2.grid(column=1, row=5)

'''
Other inputs:
00 - VIDEO1/STB/DVR
01 - VIDEO2/CBL/SAT
02 - VIDEO3/GAME
03 - VIDEO4/AUX
04 - VIDEO5
10 - DVD/BD
11 - STRM BOX
12 - TV
2D - AIRPLAY
2E - BLUETOOTH
55 - HDMI5
56 - HDMI6
57 - HDMI7
'''

################################################################################
# LABEL 6 & LISTENING MODE DROPDOWN SELECTION

l6 = Label(root,
           text='Listening Mode')
l6.grid(column=0, row=6)

# options and set default value
lm_dict = {
    'STEREO': '00',
    'DIRECT': '01',
    'SURROUND': '02',
    'FILM': '03',
    'ACTION': '05',
    'ALL CH STEREO': '0C',
}
lm_options = [
    'STEREO','DIRECT','FILM','ACTION','ALL CH STEREO'
]
listening_mode = StringVar()
listening_mode.set(lm_options[0])

# change listening mode
def change_listening_mode(mode):
    mode = listening_mode.get()
    send_command('LMD' + str(lm_dict[mode]))

# drop down menu
lm_options = OptionMenu(root,
                        listening_mode, # variable
                        *lm_options, # values
                        command=change_listening_mode, # command
                        )
lm_options.grid(column=1, row=6)

root.mainloop()
