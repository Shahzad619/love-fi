document.addEventListener('DOMContentLoaded', () => {
    const sidebar = document.getElementById('sidebar');
    const main = document.getElementById('main-content');
    const toggle = document.querySelector('.menu-toggle');
    const close = document.querySelector('.close-btn');

    toggle.onclick = () => {
        sidebar.classList.add('open');
        main.classList.add('shifted');
    };

    close.onclick = () => {
        sidebar.classList.remove('open');
        main.classList.remove('shifted');
    };

    // Close on outside click
    document.addEventListener('click', (e) => {
        if (sidebar.classList.contains('open') && 
            !sidebar.contains(e.target) && 
            !toggle.contains(e.target)) {
            sidebar.classList.remove('open');
            main.classList.remove('shifted');
        }
    });

    // Piggy bank refresh
    setInterval(() => {
        fetch('/get-bank')
            .then(r => r.text())
            .then(bank => {
                const display = document.querySelector('.piggy-display strong');
                if (display) display.innerText = bank;
            });
    }, 5000);
});

function unblockWiFi() {
    fetch('/unblock-wifi', { method: 'POST' });
    window.location.reload();
}