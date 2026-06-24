# config.py

import os
import socket

def get_local_ip():
    """
    Automatically detect the PC's LAN IP address (e.g. 192.168.1.12).
    This is used to embed into QR codes so phones can reach the server.
    Falls back to 127.0.0.1 if detection fails.
    """
    try:
        # Connect to an external address (doesn't actually send data)
        # just to find which local interface is used for LAN
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return '127.0.0.1'

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'acadscan-secret-key-2024')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # QR expiry: 3 minutes
    QR_EXPIRY_SECONDS = 180

    # Auto-detect local network IP for embedding in QR codes
    # This ensures the QR URL works from phones on the same WiFi
    SERVER_IP = os.environ.get('SERVER_IP', get_local_ip())
    SERVER_PORT = 5000

    STATIC_FOLDER = 'static'
    TEMPLATE_FOLDER = 'templates'