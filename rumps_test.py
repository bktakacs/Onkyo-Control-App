# --- Rumps Onkyo App --- #
# Author: Ben Takacs
# With the help of: ChatGPT
# Python 3.13.3

# --- Fix App Somehow --- #
import os
import sys

if hasattr(sys, '_MEIPASS'):
    os.chdir(sys._MEIPASS)
elif getattr(sys, 'frozen', False):
    # When running from a .app bundle
    bundle_dir = os.path.abspath(os.path.dirname(sys.executable))
    os.chdir(bundle_dir)


# --- Imports --- #
import rumps
rumps.debug_mode(False)
from pynput import keyboard
import threading
import time
import socket
import datetime


# --- Onkyo Information --- #
receiver_ip = "192.168.50.164"
receiver_port = 60128


# --- Onkyo Commands --- #
verbosity = False # for debugging

def build_iscp_message(command):
    # Prepare ISCP message
    header = b'ISCP'                             # 4 bytes
    header += b'\x00\x00\x00\x10'               # Header size (16 bytes)
    message = f'!1{command}'.encode('ascii') + b'\x0D'  # Add carriage return
    data_size = len(message).to_bytes(4, 'big')         # Payload size

    # Version + reserved (4 bytes) = 0x01, 0x00, 0x00, 0x00
    header += data_size + b'\x01\x00\x00\x00'
    return header + message

def send_command(
        command,
        ip="192.168.50.164",
        port=60128
):
    
    msg = build_iscp_message(command)
    print(f"Sending to {ip}:{port} → {command}")
    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(3)
            sock.connect((ip, port))
            sock.sendall(msg)
            print("✅ Command {} sent at {}".format(command, datetime.datetime.now()))
    except Exception as e:
        print(f"❌ Error: {e}")

def query_onkyo(
        command,
        ip="192.168.50.164",
        port=60128,
        timeout=3,
        verbose=True,
        expected_prefix=None,
):
    '''
    Send a query or control command to Onkyo, return raw decoded response
    '''
    msg = build_iscp_message(command)
    if verbose:
        print(f"Querying {ip}:{port} → {command}")
    
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            sock.connect((ip, port))
            sock.sendall(msg)

            # Try receiving multiple packets (for late responses)
            raw_data = b""
            for _ in range(4):
                try:
                    chunk = sock.recv(1024)
                    if not chunk:
                        break
                    raw_data += chunk
                except socket.timeout:
                    break

            decoded = raw_data.decode(errors="ignore")
            if verbose:
                print("✅ Raw response received:")
                print(decoded.strip())

            # Filter expected response
            if expected_prefix:
                for line in decoded.splitlines():
                    if expected_prefix in line:
                        return line.strip()
            return decoded.strip()
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def get_power_status():
    try:
        power_status = query_onkyo('PWRQSTN', expected_prefix='!1PWR', verbose=verbosity).split('!1PWR')[1][:2]
        return 'On' if power_status == '01' else 'Standby' if power_status == '00' else None
    except Exception as e:
        print(e)

def get_current_volume():
    try:
        volume = query_onkyo('MVLQSTN', expected_prefix='!1MVL', verbose=verbosity).split('!1MVL')[1][:2]
        return int(volume, 16)
    except Exception as e:
        print(e)

def set_volume(vol):
    vol = max(0, min(60, vol))  # redundancy Clamp between 0 and 60
    hex_val = f"{vol:02X}"
    send_command(f"MVL{hex_val}")

def get_mute_status():
    try:
        mute_status = query_onkyo('AMTQSTN', expected_prefix='!1AMT', verbose=verbosity).split('!1AMT')[1][:2]
        return 'On' if mute_status == '01' else 'Off' if mute_status == '00' else None
    except Exception as e:
        print(e)


# --- Get Current Statuses --- #
power_status = get_power_status()
volume = get_current_volume()
mute_status = get_mute_status()


# --- Rumps Setup --- #
class OnkyoStatusBarApp(rumps.App):
    def __init__(self):
        super(OnkyoStatusBarApp, self).__init__(name='Onkyo Status Bar App', title='Vol: --', quit_button=None)

        # Create menu items which can be updated later
        self.power_item = rumps.MenuItem("Toggle Power (-)", callback=self.toggle_power)
        self.mute_item = rumps.MenuItem("Toggle Mute (-)", callback=self.toggle_mute)

        self.volup_item = rumps.MenuItem("Increase Volume", callback=self.increase_volume)
        self.voldn_item = rumps.MenuItem("Decrease Volume", callback=self.decrease_volume)

        self.audio_pc_item = rumps.MenuItem('mac Mini (PC)', callback=lambda _: self.select_audio_input('05'))
        self.audio_ph_item = rumps.MenuItem('Record Player (PHONO)', callback=lambda _: self.select_audio_input('22'))

        self.lst_mode_stereo = rumps.MenuItem('STEREO', callback=lambda _: self.select_listening_mode('00'))
        self.lst_mode_action = rumps.MenuItem('ACTION', callback=lambda _: self.select_listening_mode('05'))

        self.instruction1 = rumps.MenuItem("Volume Up: Alt-R + Home")
        self.instruction2 = rumps.MenuItem("Volume Down: Alt-R + End")
        self.instruction3 = rumps.MenuItem("Toggle Mute: Alt-R + PgDn")

        # Submenus for inputs
        audio_input_menu = (
            self.audio_pc_item,
            self.audio_ph_item,
        )

        listening_mode_menu = (
            self.lst_mode_stereo,
            self.lst_mode_action,
        )

        # Assign top-level menu
        self.menu = [
            self.power_item,
            self.mute_item,
            None,
            self.volup_item,
            self.voldn_item,
            None,
            ('Audio Input', audio_input_menu),
            ('Listening Mode', listening_mode_menu),
            None,
            self.instruction1,
            self.instruction2,
            self.instruction3,
            None,
            rumps.MenuItem("Quit", callback=self.quit_app)
        ]

        self.power_status = power_status
        self.current_volume = volume
        self.mute_status = mute_status

        self.update_power_status()
        self.update_mute_status()
        self.audio_pc_item.state = 1
        self.lst_mode_stereo.state = 1

        self.keep_running = True

        self.pressed_keys = set()
        threading.Thread(target=self.start_key_listener, daemon=True).start()
        threading.Thread(target=self.poll_volume_loop, daemon=True).start()
        threading.Thread(target=self.poll_power_mute_loop, daemon=True).start()

        self.icon = 'on.jpg'

    # --- Update Items --- #
    def update_title(self):
        if self.current_volume is not None:
            self.title = f"Vol: {self.current_volume}"
        else:
            self.title = "Vol: --"

    def update_power_status(self):
        if self.power_status is not None:
            self.power_item.title = 'Toggle Power ({})'.format(self.power_status)

    def update_mute_status(self):
        if self.mute_status is not None:
            self.mute_item.title = 'Toggle Mute ({})'.format(self.mute_status)

    # --- Command Methods --- #
    def increase_volume(self, _):
        if self.current_volume is not None:
            self.current_volume = min(self.current_volume + 2, 60)
            self.update_title()
            set_volume(self.current_volume)

    def decrease_volume(self, _):
        if self.current_volume is not None:
            self.current_volume = max(self.current_volume - 2, 0)
            self.update_title()
            set_volume(self.current_volume)

    def toggle_power(self, _):
        send_command('PWR00' if self.power_status == 'On' else 'PWR01')
        self.update_power_status()

    def toggle_mute(self, _):
        send_command('AMT00' if self.mute_status == 'On' else 'AMT01')
        rumps.notification(title='Onkyo Control App', subtitle='Mute Status: {}'.format('On' if self.mute_status == 'Off' else 'Off'), message='Mute has been toggled {}.'.format(str('On' if self.mute_status == 'Off' else 'Off').lower()), data=None, sound=True)
        self.update_mute_status()

    def select_audio_input(self, input):
        send_command('SLI' + input)
        self.audio_pc_item.state = 1 if input == '05' else 0
        self.audio_ph_item.state = 1 if input == '22' else 0

    def select_listening_mode(self, input):
        send_command('LMD' + input)
        self.lst_mode_stereo.state = 1 if input == '00' else 0
        self.lst_mode_action.state = 1 if input == '05' else 0


    # --- Loop Methods --- #
    def poll_volume_loop(self):
        while self.keep_running:
            vol = get_current_volume()
            if vol is not None:
                self.current_volume = vol
                self.update_title()
            time.sleep(1)
    
    def poll_power_mute_loop(self):
        while self.keep_running:
            power_status = get_power_status()
            if power_status is not None:
                self.power_status = power_status
                self.update_power_status()

            mute_status = get_mute_status()
            if mute_status is not None:
                self.mute_status = mute_status
                self.update_mute_status()

            # if power_status == None or mute_status == None:
            #     print(power_status)
            #     print(mute_status)
            time.sleep(5)


    # --- Quit App --- #
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
            if keyboard.Key.alt_r in self.pressed_keys and key == keyboard.Key.page_down:
                self.toggle_mute(None)
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


# --- Main Loop --- #
OnkyoStatusBarApp().run()