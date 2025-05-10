import socket

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
            print("✅ Command {} sent.".format(command))
    except Exception as e:
        print(f"❌ Error: {e}")

def query_onkyo(
        command, ip="192.168.50.164"
):
    '''
    Send a query or control command to Onkyo, return raw decoded response
    '''
    pass

def db_to_hex(vol_db):
    steps = int(vol_db * 2)
    return f"{steps:02X}"  # 2-digit uppercase hex


# Example

# Example: Power ON
receiver_ip = "192.168.50.164"
receiver_port = 60128
volume = 40
# command = "MVL" + str(db_to_hex(volume / 2))  # Add other codes like "PWR00", "MVL0A", etc.
command = "PWR01"
# send_command(receiver_ip, receiver_port, command)

get_power_status(receiver_ip)