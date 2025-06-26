# --- Rumps Onkyo App --- #
# Author: Ben Takacs
# With the help of: ChatGPT
# Python 3.13.3


# --- Imports --- #
import rumps
from onkyo_controller import *
from pynput import keyboard
import threading
import time


# --- Onkyo Commands --- #
verbosity = False # for debugging

def get_power_status():
    try:
        power_status = query_onkyo('PWRQSTN', expected_prefix='!1PWR', verbose=verbosity).split('!1PWR')[1][:2]
        return power_status
    except:
        print('Error: ' + query_onkyo('PWRQSTN', expected_prefix='!1PWR', verbose=True))

def get_current_volume():
    try:
        volume = query_onkyo('MVLQSTN', expected_prefix='!1MVL', verbose=verbosity).split('!1MVL')[1][:2]
        return int(volume, 16)
    except:
        print('Error: ' + query_onkyo('MVLQSTN', expected_prefix='!1MVL', verbose=True))

def get_mute_status():
    try:
        mute_status = query_onkyo('AMTQSTN', expected_prefix='!1AMT', verbose=verbosity).split('!1AMT')[1][:2]
        return mute_status
    except:
        print('Error: ' + query_onkyo('AMTQSTN', expected_prefix='!1AMT', verbose=True))

def set_volume(vol):
    vol = max(0, min(60, vol))  # Clamp between 0 and 80
    hex_val = f"{vol:02X}"
    send_command(f"MVL{hex_val}")

# --- Get Current Status --- #
power_status_code = get_power_status()
power_status = 'On' if power_status_code == '01' else 'Standby'
volume = get_current_volume()
mute_status_code = get_mute_status()
mute_status = 'On' if mute_status_code == '01' else 'Off'


# --- Rumps Setup --- #
class OnkyoStatusBarApp(rumps.App):
    def __init__(self):
        super(OnkyoStatusBarApp, self).__init__('Onkyo Status Bar App', title='音響 Vol: --', quit_button=None)
        self.menu = [
            rumps.MenuItem("Toggle Power (-)", callback=self.toggle_power, key="power"),
            rumps.MenuItem("Toggle Mute (-)", callback=self.toggle_mute, key='mute'),
            None,
            rumps.MenuItem("Increase Volume", callback=self.increase_volume, key='volup'),
            rumps.MenuItem("Decrease Volume", callback=self.decrease_volume, key='voldown'),
            None,
            rumps.MenuItem("Control Volume with Alt-R + Home (Up) or End (Down)"),
            rumps.MenuItem("Quit", callback=self.quit_app)
        ]
        self.power_status = power_status
        self.current_volume = volume
        self.mute_status = mute_status

        self.keep_running = True

        self.pressed_keys = set()
        threading.Thread(target=self.start_key_listener, daemon=True).start()
        threading.Thread(target=self.poll_volume_loop, daemon=True).start()
        # threading.Thread(target=self.poll_power_mute, daemon=True).start()

    def update_title(self):
        if self.current_volume is not None:
            self.title = f"音響 Vol: {self.current_volume}"
        else:
            self.title = "音響 Vol: --"

    def update_power_status(self):
        if self.power_status is not None:
            self.menu["power"].title = 'Toggle Power ({})'.format(self.power_status)

    def increase_volume(self, _):
        if self.current_volume is not None:
            self.current_volume = min(self.current_volume + 2, 60)
            set_volume(self.current_volume)
            self.update_title()
            # send_command('MVL' + str(db_to_hex(self.current_volume / 2)))

    def decrease_volume(self, _):
        if self.current_volume is not None:
            self.current_volume = max(self.current_volume - 2, 0)
            set_volume(self.current_volume)
            self.update_title()

    def toggle_power(self, _):
        send_command('PWR00' if self.power_status == '01' else 'PWR01')
        self.update_power_status()

    def toggle_mute(self, _):
        send_command('AMT00' if self.mute_status == '01' else 'AMT01')
        self.update_power_status()

    def poll_volume_loop(self):
        while self.keep_running:
            vol = get_current_volume()
            if vol is not None:
                self.current_volume = vol
                self.update_title()
            time.sleep(1)

    # def poll_power_mute(self):
    #     while self.keep_running:
    #         app_power_status = get_power_status()
    #         if app_power_status is not None:
                


    def quit_app(self, _):
        self.keep_running = False
        rumps.quit_application()
    
    # --- Key Listener --- #
    def on_key_press(self, key):
        self.pressed_keys.add(key)
        try:
            if keyboard.Key.alt_r in self.pressed_keys and key == keyboard.Key.home:
                self.increase_volume(None)
            if keyboard.Key.alt_r in self.pressed_keys and key == keyboard.Key.end:
                self.decrease_volume(None)
        except AttributeError:
            pass

    def on_key_release(self, key):
        self.pressed_keys.discard(key)

    def start_key_listener(self):
        listener = keyboard.Listener(
            on_press=self.on_key_press,
            on_release=self.on_key_release,
        )
        listener.daemon = True
        listener.start()


# --- Global Keypresss Recognition --- #
# current_keys = set()
# vol = OnkyoStatusBarApp.poll_volume_loop
# def on_press(key):
#     try:
#         if key == keyboard.Key.home and keyboard.Key.alt_r in current_keys:
#             increase_volume()
#         elif key == keyboard.Key.end and keyboard.Key.alt_r in current_keys:
#             decrease_volume()
#         current_keys.add(key)
#     except AttributeError:
#         pass

# def on_release(key):
#     current_keys.discard(key)

# def start_key_listener():
#     listener = keyboard.Listener(on_press=on_press, on_release=on_release)
#     listener.daemon = True
#     listener.start()

# start_key_listener()

OnkyoStatusBarApp().run()