from flask import Flask, render_template, request, redirect, session
import threading
import time
import random
import time
from collections import defaultdict
from datetime import datetime, timedelta, date
import json

app = Flask(__name__)
app.secret_key = 'love-fi-secret-2025'

# ALL IN SECONDS
total_timer = 0        # seconds
remaining_time = 0     # seconds
piggy_bank = 0
daily_limit = 90
gifts = []  # List to store gifts
# STREAK SYSTEM
last_save_date = None
current_streak = 0

# PASSWORD SYSTEM
PARENT_PASSWORD = "love123"
current_code = None

def generate_code():
    global current_code
    current_code = str(random.randint(1000, 9999))
    print(f"PARENT CODE (SEND TO PHONE): {current_code}")


DATA_FILE = 'data.json'

def load_data():
    global piggy_bank, current_streak, last_save_date, gifts, total_timer, remaining_time
    try:
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
            piggy_bank = data.get('piggy_bank', 0)
            current_streak = data.get('current_streak', 0)
            last_save_date = data.get('last_save_date')
            if last_save_date:
                last_save_date = date.fromisoformat(last_save_date)
            gifts = data.get('gifts', [])
            total_timer = data.get('total_timer', 0)
            remaining_time = data.get('remaining_time', 0)
        print("Data loaded from file")
    except FileNotFoundError:
        print("No data file — starting fresh")
    except Exception as e:
        print(f"Load error: {e}")

def save_data():
    data = {
        'piggy_bank': piggy_bank,
        'current_streak': current_streak,
        'last_save_date': last_save_date.isoformat() if last_save_date else None,
        'gifts': gifts,
        'total_timer': total_timer,
        'remaining_time': remaining_time
    }
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        print("Data saved to file")
    except Exception as e:
        print(f"Save error: {e}")


   # ← PUT THIS AFTER generate_code(), BEFORE @app.route('/graph')
def get_usage_logs():
    try:
        with open('usage_log.json', 'r') as f:
            return json.load(f)
    except:
        return []
    
    # Create dummy log if file doesn't exist
try:
    with open('usage_log.json', 'x') as f:
        json.dump([
            {"action": "used", "minutes": 30, "timestamp": time.time() - 86400},
            {"action": "saved", "minutes": 10, "timestamp": time.time() - 86400 * 2},
            {"action": "used", "minutes": 45, "timestamp": time.time() - 86400 * 3},
        ], f)
except:
    pass

@app.route('/')
def home():
    return "LoveFi is running! Go to /to-parent", 200

@app.route('/health')
def health():
    return "OK", 200
    


@app.route('/')
def home():
    return redirect('/parent')

@app.route('/parent')
def parent():
    if not session.get('authenticated'):
        return redirect('/to-parent')
    
    # Refresh activity
    session['last_activity'] = time.time()
    
    last_minutes = total_timer // 60 if total_timer > 0 else 60
    return render_template('parent.html', piggy_bank=piggy_bank, last_timer=last_minutes)

@app.route('/set-timer', methods=['POST'])
def set_timer():
    global total_timer, remaining_time
    minutes = int(request.form['minutes'])
    total_timer = minutes * 60      # convert to seconds
    remaining_time = total_timer    # seconds
    generate_code()
    save_data()
    return redirect('/kid')

@app.route('/kid')
def kid():
    session.pop('authenticated', None)
    session.pop('last_activity', None)
    return render_template(
        'kid.html',
        remaining_seconds=remaining_time,
        piggy_bank=piggy_bank,
        code=current_code,
        gifts=gifts  # ← THIS MUST BE PASSED!
    )  


@app.route('/save-time', methods=['POST'])
def save_time():
    global piggy_bank, last_save_date, current_streak
    used = int(request.form['used'])
    today = datetime.now().date()

    # Check if saved today
    if last_save_date != today:
        # New day
        if last_save_date == today - timedelta(days=1):
            current_streak += 1  # Continue streak
        else:
            current_streak = 1  # New streak
        last_save_date = today

    if used < daily_limit:
        piggy_bank = min(20, piggy_bank + 5)
        save_data()

    return redirect('/parent')

@app.route('/gift-time', methods=['POST'])
def gift_time():
    global remaining_time
    minutes = int(request.form['gift_minutes'])
    seconds_to_add = minutes * 60  # convert here only
    
    remaining_time += seconds_to_add  # already in seconds
    
    message = request.form['love_note'].strip() or "Extra time for being awesome!"
    
    gifts.append({
        'minutes': minutes,
        'message': message,
        'time': time.strftime("%I:%M %p")
    })
    save_data()
    return redirect('/parent')

@app.route('/reset-timer', methods=['POST'])
def reset_timer():
    global total_timer, remaining_time
    total_timer = 0
    remaining_time = 0
    save_data()
    return redirect('/parent')

@app.route('/get-bank')
def get_bank():
    return str(piggy_bank)

@app.route('/get-streak')
def get_streak():
    return {
        'streak': current_streak,
        'badges': [
            {'name': '1-Day Hero', 'icon': 'trophy', 'unlocked': current_streak >= 1},
            {'name': '3-Day Pro', 'icon': 'fire', 'unlocked': current_streak >= 3},
            {'name': '7-Day Legend', 'icon': 'star', 'unlocked': current_streak >= 7},
        ]
    }

@app.route('/to-parent', methods=['GET', 'POST'])
def to_parent():
    # Auto-logout after 60 seconds
    if session.get('authenticated'):
        last_activity = session.get('last_activity', 0)
        if time.time() - last_activity > 60:
            session.clear()
            return render_template('password.html', error="Session expired. Enter password again.")

    if request.method == 'POST':
        password = request.form['password']
        if password == PARENT_PASSWORD:
            session['authenticated'] = True
            session['last_activity'] = time.time()
            return redirect('/parent')
        else:
            return render_template('password.html', error="Wrong password!")
    
    return render_template('password.html')

# COUNTDOWN: SUBTRACT 1 SECOND
def countdown():
    global remaining_time
    while True:
        time.sleep(1)
        if remaining_time > 0:
            remaining_time -= 1  # 1 second

threading.Thread(target=countdown, daemon=True).start()
@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect('/to-parent')

@app.route('/graph')
def graph():
    if not session.get('authenticated'):  # ← FIXED
        return redirect('/to-parent')

    logs = get_usage_logs()
    today = datetime.now().date()

    def group_data(days):
        data = defaultdict(lambda: {'used': 0, 'saved': 0})
        cutoff = today - timedelta(days=days)
        for log in logs:
            log_date = datetime.fromtimestamp(log['timestamp']).date()
            if log_date >= cutoff:
                key = log_date.strftime({
                    7: '%a',
                    30: '%d %b',
                    365: '%b %Y'
                }[days])
                if log['action'] == 'used':
                    data[key]['used'] += log['minutes']
                elif log['action'] == 'saved':
                    data[key]['saved'] += log['minutes']
        labels = list(data.keys())
        used = [data[k]['used'] for k in labels]
        saved = [data[k]['saved'] for k in labels]
        return {'labels': labels, 'used': used, 'saved': saved}

    return render_template('graph.html',
                           week_data=group_data(7),
                           month_data=group_data(30),
                           year_data=group_data(365))


@app.route('/get-gifts')
def get_gifts():
    return {
        'piggy_bank': piggy_bank,
        'list': gifts
    }


@app.route('/how-it-works')
def how_it_works():
    if not session.get('authenticated'):
        return redirect('/to-parent')
    return render_template('how_it_works.html')


@app.route('/why-lovefi')
def why_lovefi():
    if not session.get('authenticated'):
        return redirect('/to-parent')
    return render_template('why_lovefi.html')

@app.route('/unblock-wifi', methods=['POST'])
def unblock_wifi():
    global remaining_time
    remaining_time = 60  # 1 hour unblock
    save_data()
    return 'OK'


# LOAD DATA ON START
load_data()

# AUTO-SAVE EVERY 10 SECONDS
def auto_save():
    while True:
        time.sleep(10)
        save_data()

threading.Thread(target=auto_save, daemon=True).start()

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
    
    # FOR RENDER: Keep alive
    import threading
    import time
    def keep_alive():
        while True:
            time.sleep(60)
            print("Keep-alive ping")
    threading.Thread(target=keep_alive, daemon=True).start()