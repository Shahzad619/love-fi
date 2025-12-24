document.addEventListener('DOMContentLoaded', () => {
    const countdownEl = document.getElementById('countdown');
    const bankEl = document.getElementById('bank');
    const streakEl = document.getElementById('streak-count'); // If you have streak display
    const popup = document.getElementById('love-popup');
    const messageEl = document.getElementById('love-message');
    const minutesEl = document.getElementById('gift-minutes');
    const heartsContainer = document.getElementById('hearts');

    let lastGiftCount = 0;
    let wasTimerEverSet = false;

    function formatTime(seconds) {
        if (seconds <= 0) return "00:00:00";
        const h = Math.floor(seconds / 3600).toString().padStart(2, '0');
        const m = Math.floor((seconds % 3600) / 60).toString().padStart(2, '0');
        const s = (seconds % 60).toString().padStart(2, '0');
        return `${h}:${m}:${s}`;
    }

    function showLove(gift) {
        messageEl.innerText = gift.message || "You're awesome!";
        minutesEl.innerText = gift.minutes;
        heartsContainer.innerHTML = '';
        for (let i = 0; i < 6; i++) {
            const heart = document.createElement('div');
            heart.className = 'heart';
            heart.innerHTML = '❤️';
            heart.style.animationDelay = `${i * 0.1}s`;
            heartsContainer.appendChild(heart);
        }
        popup.classList.add('show');
        setTimeout(() => popup.classList.remove('show'), 5000);
    }

    function updateAll() {
        // Fetch gifts + piggy (your existing endpoint works!)
        fetch('/get-gifts')
            .then(r => r.json())
            .then(data => {
                bankEl.innerText = data.piggy_bank;

                if (data.list.length > lastGiftCount) {
                    const newGifts = data.list.slice(lastGiftCount);
                    newGifts.forEach(showLove);
                    lastGiftCount = data.list.length;
                }
            });

        // Simple fetch for current remaining time (we'll add this tiny route)
        fetch('/current-time')
            .then(r => r.json())
            .then(data => {
                const seconds = data.remaining;
                const totalEver = data.total_timer;

                if (totalEver > 0) wasTimerEverSet = true;

                countdownEl.innerHTML = formatTime(seconds);

                if (seconds <= 0) {
                    if (wasTimerEverSet) {
                        countdownEl.innerHTML = "WiFi Blocked!";
                        countdownEl.style.color = '#e74c3c';
                        document.body.style.background = 'linear-gradient(135deg, #e74c3c, #c0392b)';
                        document.body.style.pointerEvents = 'none';
                        const parentBtn = document.querySelector('.btn-parent');
                        if (parentBtn) {
                            parentBtn.style.pointerEvents = 'auto';
                            parentBtn.style.opacity = '1';
                        }
                    } else {
                        countdownEl.innerHTML = "Set Timer from Parent";
                        countdownEl.style.color = '#666';
                        document.body.style.background = '#f8f9fa';
                    }
                }
            })
            .catch(err => console.log('Update error:', err));
    }

    // Run every second for smooth countdown
    setInterval(updateAll, 1000);
    updateAll(); // First immediate update
});