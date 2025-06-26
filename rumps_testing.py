import unittest
from unittest.mock import patch, MagicMock
import socket
from rumps_app import (
    build_iscp_message,
    send_command,
    query_onkyo
)

class TestOnkyoApp(unittest.TestCase):

    def test_build_iscp_message_format(self):
        command = "MVLUP"
        msg = build_iscp_message(command)

        self.assertTrue(msg.startswith(b'ISCP'))
        self.assertIn(b'!1MVLUP\x0D', msg)
        self.assertEqual(msg[4:8], b'\x00\x00\x00\x10')  # Header size
        self.assertEqual(msg[12:16], b'\x01\x00\x00\x00')  # Version/reserved

    @patch('socket.socket')
    def test_send_command_success(self, mock_socket):
        mock_sock = MagicMock()
        mock_socket.return_value.__enter__.return_value = mock_sock

        send_command("MVLUP")
        mock_sock.connect.assert_called()
        mock_sock.sendall.assert_called()

    @patch('socket.socket')
    def test_query_onkyo_response_parsing(self, mock_socket):
        fake_response = b'ISCP\x00\x00\x00\x10' + b'\x00'*12 + b'!1MVLUP\x0D'
        mock_sock = MagicMock()
        mock_sock.recv.side_effect = [fake_response, b'']
        mock_socket.return_value.__enter__.return_value = mock_sock

        response = query_onkyo("MVLUP", verbose=False)
        self.assertIn("!1MVLUP", response)

    @patch('socket.socket')
    def test_query_onkyo_timeout(self, mock_socket):
        mock_sock = MagicMock()
        mock_sock.recv.side_effect = socket.timeout
        mock_socket.return_value.__enter__.return_value = mock_sock

        response = query_onkyo("MVLUP", verbose=False)
        self.assertEqual(response, None)

if __name__ == '__main__':
    unittest.main()