// static/js/script.js - AcadScan frontend scripts

// ── Flash message auto-dismiss ──
// Flash alerts disappear automatically after 5 seconds
document.addEventListener('DOMContentLoaded', function () {
  const alerts = document.querySelectorAll('.alert');
  alerts.forEach(function (alert) {
    setTimeout(function () {
      alert.style.transition = 'opacity 0.5s ease';
      alert.style.opacity = '0';
      setTimeout(function () {
        alert.remove();
      }, 500);
    }, 5000); // 5 seconds
  });

  // ── QR Countdown Timer ──
  // If a countdown element exists on the page, start counting down
  const countdown = document.getElementById('qr-countdown');
  if (countdown) {
    let seconds = parseInt(countdown.getAttribute('data-seconds'), 10);
    const bar = document.getElementById('expiry-bar');

    const totalSeconds = seconds;

    const interval = setInterval(function () {
      seconds -= 1;
      if (seconds <= 0) {
        clearInterval(interval);
        countdown.textContent = 'EXPIRED';
        countdown.style.color = 'var(--danger)';
        if (bar) bar.style.width = '0%';
        const notice = document.getElementById('expired-notice');
        if (notice) notice.style.display = 'block';
      } else {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        countdown.textContent = `${mins}:${secs.toString().padStart(2, '0')}`;
        if (bar) {
          const pct = (seconds / totalSeconds) * 100;
          bar.style.width = pct + '%';
          bar.style.background = pct > 40 ? 'var(--success)' : 'var(--warning)';
        }
      }
    }, 1000);
  }

  // ── Copy QR text to clipboard ──
  const copyBtn = document.getElementById('copy-qr-btn');
  if (copyBtn) {
    copyBtn.addEventListener('click', function () {
      const qrText = document.getElementById('qr-raw-text');
      if (qrText) {
        navigator.clipboard.writeText(qrText.value).then(function () {
          copyBtn.textContent = '✅ Copied!';
          setTimeout(function () {
            copyBtn.textContent = '📋 Copy QR Code Text';
          }, 2000);
        });
      }
    });
  }
});