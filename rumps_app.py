# --- Rumps Onkyo App --- #
# Author: Ben Takacs
# With the help of: ChatGPT
# Python 3.13.3

# --- Imports --- #
import rumps
rumps.debug_mode(True)
from pynput import keyboard
import threading
import time
import socket
import datetime
import os
import sys
import subprocess


# --- Fix App Somehow --- #
if hasattr(sys, '_MEIPASS'):
    os.chdir(sys._MEIPASS)
elif getattr(sys, 'frozen', False):
    # When running from a .app bundle
    bundle_dir = os.path.abspath(os.path.dirname(sys.executable))
    os.chdir(bundle_dir)

def check_accessibility_permissions():
    result = subprocess.run(
        ['osascript', '-e', 'tell application "System Events" to return UI elements enabled'],
        capture_output=True,
        text=True
    )
    if result.stdout.strip() != 'true':
        print("Accessibility permissions are not enabled. Please enable them in System Preferences.")


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
        ip=receiver_ip,
        port=receiver_port
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
        ip=receiver_ip,
        port=receiver_port,
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
        super(OnkyoStatusBarApp, self).__init__(name='Onkyo Control App', title='Vol: --', quit_button=None)

        # Create menu items which can be updated later
        # power & mute toggle
        self.power_item = rumps.MenuItem("Toggle Power\t(-)", callback=self.toggle_power)
        self.mute_item = rumps.MenuItem("Toggle Mute\t(-)", callback=self.toggle_mute)

        # volume 
        self.volup_item = rumps.MenuItem("Increase Volume", callback=self.increase_volume)
        self.voldn_item = rumps.MenuItem("Decrease Volume", callback=self.decrease_volume)

        # audio input
        self.audio_pc_item = rumps.MenuItem('Mac Mini (PC)', callback=lambda _: self.select_audio_input('05'))
        self.audio_ph_item = rumps.MenuItem('Record Player (PHONO)', callback=lambda _: self.select_audio_input('22'))
        self.audio_bt_item = rumps.MenuItem('Bluetooth (BT)', callback=lambda _: self.select_audio_input('2E'))
        self.audio_ap_item = rumps.MenuItem('Airplay (AIR)', callback=lambda _: self.select_audio_input('2D'))

        # input selection
        self.lst_mode_stereo = rumps.MenuItem('STEREO', callback=lambda _: self.select_listening_mode('00'))
        # self.lst_mode_film = rumps.MenuItem('FILM', callback=lambda _: self.select_listening_mode('03'))
        self.lst_mode_action = rumps.MenuItem('ACTION', callback=lambda _: self.select_listening_mode('05'))


        # control instructions
        self.instruction1 = rumps.MenuItem('Volume Up:\t\tAlt-R + Home')
        self.instruction2 = rumps.MenuItem('Volume Down:\tAlt-R + End')
        self.instruction3 = rumps.MenuItem('Toggle mute:\t\tAlt-R + PgUp')


        # Submenus for inputs
        audio_input_menu = (
            self.audio_pc_item,
            self.audio_ph_item,
            self.audio_bt_item,
            self.audio_ap_item,
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
            self.power_item.title = 'Toggle Power\t({})'.format(self.power_status)

    def update_mute_status(self):
        if self.mute_status is not None:
            self.mute_item.title = 'Toggle Mute\t({})'.format(self.mute_status)

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

    def toggle_listening_mode(self, _):
        lm = '05' if self.lst_mode_stereo.state == 1 else '00' if self.lst_mode_action.state == 1 else None # 00 for stereo, 05 for action, so send opposite command to toggle. will need updating if more listening modes added
        self.select_listening_mode(lm)


    def select_audio_input(self, input):
        send_command('SLI' + input)
        self.audio_pc_item.state = 1 if input == '05' else 0
        self.audio_ph_item.state = 1 if input == '22' else 0
        self.audio_bt_item.state = 1 if input == '2E' else 0
        self.audio_ap_item.state = 1 if input == '2D' else 0

    def select_listening_mode(self, input):
        send_command('LMD' + input)
        self.lst_mode_stereo.state = 1 if input == '00' else 0
        # self.lst_mode_film.state   = 1 if input == '03' else 0
        self.lst_mode_action.state = 1 if input == '05' else 0


    # --- Loop Methods --- #
    def poll_volume_loop(self):
        while self.keep_running:
            vol = get_current_volume()
            if vol is not None:
                self.current_volume = vol
                self.update_title()
            time.sleep(10)
    
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

            time.sleep(5)


    # --- Quit App --- #
    def quit_app(self, _):
        self.keep_running = False
        rumps.quit_application()
    

# --- Setup Keybinds --- #
pressed_keys = set()

def on_key_press(key, app_instance):
    try:
        # Add the key to the pressed keys set
        pressed_keys.add(key)

        # Check for the specific hotkey combinations
        if keyboard.Key.cmd in pressed_keys and keyboard.Key.ctrl in pressed_keys and keyboard.Key.alt in pressed_keys and keyboard.Key.shift_l in pressed_keys:
            if key == keyboard.Key.home:
                app_instance.increase_volume(None)
            elif key == keyboard.Key.end:
                app_instance.decrease_volume(None)
            elif key == keyboard.Key.page_up:
                app_instance.toggle_mute(None)
            elif key == keyboard.Key.page_down:
                app_instance.toggle_listening_mode(None)
    except AttributeError:
        pass

def on_key_release(key):
    # Remove the key from the pressed keys set
    pressed_keys.discard(key)

def start_hotkey_listener(app_instance):
    # Start the listener for key presses and releases
    with keyboard.Listener(
        on_press=lambda key: on_key_press(key, app_instance),
        on_release=on_key_release
    ) as listener:
        listener.join()

# --- Global Hotkeys Setup --- #
# def start_global_hotkeys(app_instance):
#     print("🔑 Global key listener started")
#     hotkeys = {
#         '<ctrl>+<alt>+<cmd>+<shift_l>+<home>': lambda: app_instance.increase_volume(None),
#         '<ctrl>+<alt>+<cmd>+<shift_l>+<end>': lambda: app_instance.decrease_volume(None),
#         '<ctrl>+<alt>+<cmd>+<shift_l>+<page_up>': lambda: app_instance.toggle_mute(None),
#     }
#     with keyboard.GlobalHotKeys(hotkeys) as h:
#         h.join()


# --- Run --- #
if __name__ == "__main__":

    check_accessibility_permissions()

    app_instance = OnkyoStatusBarApp()

    threading.Thread(target=start_hotkey_listener, args=(app_instance,), daemon=True).start() 
    # threading.Thread(target=start_global_hotkeys, args=(app_instance,), daemon=True).start()

    # --- Main Loop --- #
    app_instance.run()