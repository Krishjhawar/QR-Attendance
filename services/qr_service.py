# services/qr_service.py
#
# QR now embeds a full HTTP URL:
#   http://192.168.1.12:5000/attendance/mark?session_id=4
#
# Student scans with phone camera → URL opens in browser → attendance auto-marked.
# get_or_create_qr() lets teachers reopen an existing session's QR from dashboard.

import qrcode
import os

QR_DIR = os.path.join('static', 'images')


def generate_qr_code(session_id: int, server_ip: str, server_port: int = 5000):
    """
    Create QR image embedding the attendance URL.
    Returns (filename, url).
    """
    os.makedirs(QR_DIR, exist_ok=True)

    url = f"http://{server_ip}:{server_port}/attendance/mark?session_id={session_id}"

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color='black', back_color='white')
    filename = f'qr_session_{session_id}.png'
    img.save(os.path.join(QR_DIR, filename))

    return filename, url


def get_or_create_qr(session_id: int, server_ip: str, server_port: int = 5000):
    """
    Return (filename, url) for a session's QR.
    If the image already exists on disk, reuse it (no re-generation needed).
    If not (e.g. server restarted, file deleted), regenerate it.
    
    This powers the teacher "reopen QR" feature — clicking a session card
    from the dashboard shows the same QR the students should scan.
    """
    filename = f'qr_session_{session_id}.png'
    filepath = os.path.join(QR_DIR, filename)
    url      = f"http://{server_ip}:{server_port}/attendance/mark?session_id={session_id}"

    if not os.path.exists(filepath):
        # File missing — regenerate with same URL
        return generate_qr_code(session_id, server_ip, server_port)

    return filename, url