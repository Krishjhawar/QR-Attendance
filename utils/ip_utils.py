# utils/ip_utils.py
#
# WHY SESSIONS SHOW DIFFERENT IPs:
# ─────────────────────────────────
# Sessions #1/#2 → teacher opened http://127.0.0.1:5000
#   Flask saw remote_addr = 127.0.0.1  (loopback — not the real LAN IP)
# Session #3    → teacher opened http://192.168.1.12:5000
#   Flask saw remote_addr = 192.168.1.12  (actual LAN IP) ✓
#
# FIX: Normalize 127.0.0.1 → LAN IP at the point of capture.
#
# HOTSPOT SCENARIO:
# ─────────────────
# Phone hotspot creates subnet typically 192.168.43.x
# Teacher PC connected to hotspot → e.g. 192.168.43.100
# Student phone (hotspot host)   → e.g. 192.168.43.1
# compare_network() checks first 3 octets → both 192.168.43 → PASS ✓

import socket
from flask import request


def _lan_ip() -> str:
    """Detect this machine's LAN IP (works for WiFi and phone hotspot)."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))   # doesn't actually send data
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return '127.0.0.1'


def get_client_ip() -> str:
    """
    Return the real IP of the HTTP client, normalized:
      127.0.0.1 / ::1  →  actual LAN IP
    This ensures teacher sessions stored via localhost
    still compare correctly against student LAN IPs.
    """
    forwarded = request.headers.get('X-Forwarded-For', '')
    ip = forwarded.split(',')[0].strip() if forwarded else request.remote_addr

    if ip in ('127.0.0.1', '::1', 'localhost'):
        ip = _lan_ip()

    return ip


def compare_network(ip1: str, ip2: str, prefix_bits: int = 24) -> bool:
    """
    Return True if ip1 and ip2 are on the same subnet.

    Default /24 → first 3 octets must match:
      192.168.1.5   vs 192.168.1.99  → True   ✓ (same LAN)
      192.168.43.1  vs 192.168.43.5  → True   ✓ (hotspot)
      192.168.1.5   vs 10.0.0.5      → False  ✗

    prefix_bits=16 would match the full 192.168.x.x range.
    """
    # Pure loopback dev mode
    if ip1 in ('127.0.0.1', '::1') and ip2 in ('127.0.0.1', '::1'):
        return True

    try:
        octets = prefix_bits // 8
        return '.'.join(ip1.split('.')[:octets]) == '.'.join(ip2.split('.')[:octets])
    except Exception:
        return False


# Alias used throughout the codebase
is_same_network = compare_network