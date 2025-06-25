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


# --- Get Current Status --- #
power_status = get_power_status()
volume = get_current_volume()
mute_status = get_mute_status()


# --- Rumps Setup --- #
class OnkyoStatusBarApp(rumps.App):
    def __init__(self):
        super(OnkyoStatusBarApp, self).__init__('Onkyo Status Bar App', title='音響 Vol: --', quit_button=None)
        self.menu = [
            rumps.MenuItem("Increase Volume", callback=self.increase_volume),
            rumps.MenuItem("Decrease Volume", callback=self.decrease_volume),
            None,
            rumps.MenuItem("Quit", callback=self.quit_app)
        ]
        self.current_volume = volume
        self.keep_running = True
        threading.Thread(target=self.poll_volume_loop, daemon=True).start()

    def update_title(self):
        if self.current_volume is not None:
            self.title = f"Vol: {self.current_volume}"
        else:
            self.title = "Vol: --"

    # def increase_volume(self, _):
    #     if self.current_volume is not None:
    #         self.current_volume = min(self.current_volume + 2, 80)
    #         set_volume(self.current_volume)
    #         self.update_title()

    # def decrease_volume(self, _):
    #     if self.current_volume is not None:
    #         self.current_volume = max(self.current_volume - 2, 0)
    #         set_volume(self.current_volume)
            # self.update_title()
    def increase_volume(self, _):
        if self.current_volume is not None:
            try:
                self.current_volume = min(self.current_volume + 2, 60)
                send_command('MVL' + str(db_to_hex(self.current_volume / 2)))
                self.update_title()
            except:
                print('Error: Could not increase volume')

    def decrease_volume(self, _):
        if self.current_volume is not None:
            try:
                self.current_volume = max(self.current_volume - 2, 0)
                send_command('MVL' + str(db_to_hex(self.current_volume / 2)))
                self.update_title()
            except:
                print('Error: Could not increase volume')

    def poll_volume_loop(self):
        while self.keep_running:
            vol = get_current_volume()
            if vol is not None:
                self.current_volume = vol
                self.update_title()
            time.sleep(1)

    def quit_app(self, _):
        self.keep_running = False
        rumps.quit_application()


# --- Global Keypresss Recognition --- #
current_keys = set()
vol = OnkyoStatusBarApp.poll_volume_loop
def on_press(key):
    try:
        if key == keyboard.Key.home and keyboard.Key.alt_r in current_keys:
            increase_volume()
        elif key == keyboard.Key.end and keyboard.Key.alt_r in current_keys:
            decrease_volume()
        current_keys.add(key)
    except AttributeError:
        pass

def on_release(key):
    current_keys.discard(key)

def start_key_listener():
    listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    listener.daemon = True
    listener.start()

start_key_listener()

OnkyoStatusBarApp().run()