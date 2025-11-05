document.addEventListener('DOMContentLoaded', () => {
    const countdownEl = document.getElementById('countdown');
    const bankEl = document.getElementById('bank');
    const popup = document.getElementById('love-popup');
    const messageEl = document.getElementById('love-message');
    const minutesEl = document.getElementById('gift-minutes');
    const heartsContainer = document.getElementById('hearts');

    let seconds = window.remainingSeconds;
    let lastGiftCount = window.initialGiftCount || 0;  // ← FROM SERVER

    function updateTimer() {
        if (seconds <= 0) {
            countdownEl.innerHTML = "WiFi Blocked!";
            countdownEl.style.color = '#e74c3c';
            countdownEl.style.background = 'rgba(231,76,60,0.1)';
            document.body.style.background = 'linear-gradient(135deg, #e74c3c, #c0392b)';
            document.body.style.pointerEvents = 'none';
            return;
        }
        const h = Math.floor(seconds / 3600);
        const m = Math.floor((seconds % 3600) / 60);
        const s = seconds % 60;
        countdownEl.innerHTML = `${h.toString().padStart(2,'0')}:${m.toString().padStart(2,'0')}:${s.toString().padStart(2,'0')}`;
        seconds--;
    }

    function showLove(gift) {
        messageEl.innerText = gift.message;
        minutesEl.innerText = gift.minutes;
        heartsContainer.innerHTML = '';
        for (let i = 0; i < 6; i++) {
            const heart = document.createElement('div');
            heart.className = 'heart';
            heart.innerHTML = 'heart';
            heart.style.animationDelay = `${i * 0.1}s`;
            heartsContainer.appendChild(heart);
        }
        popup.classList.add('show');
        setTimeout(() => popup.classList.remove('show'), 5000);
    }

    function checkUpdates() {
        fetch('/get-gifts')
            .then(r => r.json())
            .then(data => {
                bankEl.innerText = data.piggy_bank;

                if (data.list.length > lastGiftCount) {
                    const newGifts = data.list.slice(lastGiftCount);
                    newGifts.forEach(gift => showLove(gift));
                    lastGiftCount = data.list.length;
                }
            })
            .catch(err => console.error('Fetch error:', err));
    }

    updateTimer();
    setInterval(updateTimer, 1000);
    setInterval(checkUpdates, 2000);
    checkUpdates();
});