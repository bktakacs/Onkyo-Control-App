import socket
import datetime

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

def db_to_hex(vol_db):
    steps = int(vol_db * 2)
    return f"{steps:02X}"  # 2-digit uppercase hex


# Example

# Example: Power ON
receiver_ip = "192.168.50.164"
receiver_port = 60128
# volume = 40
# command = "MVL" + str(db_to_hex(volume / 2))  # Add other codes like "PWR00", "MVL0A", etc.
# command = "MVL" + str(25)
# send_command(command)

# query_onkyo('AMTQSTN', verbose=True, expected_prefix='!1AMT')

# x = query_onkyo("PWRQSTN", expected_prefix="!1PWR", verbose=True)
# code = x.split("!1PWR")[1][:2]
# print('Device on' if code == '01' else 'Standby')
# if x == '!1PWR00' print('Device off') else 
# print('Device off') if x == '!1PWR00' else print('Device on')