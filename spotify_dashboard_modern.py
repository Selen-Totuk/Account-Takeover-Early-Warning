# spotify_dashboard_modern.py
from flask import Flask, render_template_string, jsonify
import random
import threading
import time
from datetime import datetime

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Spotify Güvenlik</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #000;
            color: #fff;
            padding: 20px;
        }
        .container { max-width: 1400px; margin: 0 auto; }
        h1 { color: #1DB954; margin-bottom: 30px; }
        .stats {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 20px;
            margin-bottom: 30px;
        }
        .card {
            background: #181818;
            padding: 25px;
            border-radius: 10px;
            border: 1px solid #282828;
        }
        .card h3 { color: #b3b3b3; font-size: 14px; margin-bottom: 10px; }
        .card .number { font-size: 36px; font-weight: bold; color: #1DB954; }
        .risk-meter {
            background: #181818;
            padding: 25px;
            border-radius: 10px;
            margin-bottom: 30px;
        }
        .risk-bar {
            width: 100%;
            height: 20px;
            background: #282828;
            border-radius: 10px;
            overflow: hidden;
            margin: 10px 0;
        }
        .risk-fill {
            height: 100%;
            width: 0%;
            background: linear-gradient(90deg, #1DB954, #ffd700, #ff4444);
            transition: width 0.5s;
        }
        .activities {
            background: #181818;
            padding: 25px;
            border-radius: 10px;
        }
        .activity {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px;
            border-bottom: 1px solid #282828;
            animation: slideIn 0.3s;
        }
        @keyframes slideIn {
            from { opacity: 0; transform: translateX(-20px); }
            to { opacity: 1; transform: translateX(0); }
        }
        .activity.high-risk { background: rgba(255, 68, 68, 0.1); }
        .risk-badge {
            padding: 5px 10px;
            border-radius: 15px;
            font-size: 12px;
            font-weight: bold;
        }
        .risk-low { background: #1DB954; color: black; }
        .risk-medium { background: #ffd700; color: black; }
        .risk-high { background: #ff4444; color: white; }
        .live-badge {
            background: #ff4444;
            padding: 5px 10px;
            border-radius: 5px;
            font-size: 12px;
            animation: pulse 2s infinite;
        }
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        .footer {
            text-align: center;
            margin-top: 30px;
            color: #666;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎵 Spotify Güvenlik Merkezi</h1>
        
        <div class="stats">
            <div class="card">
                <h3>Toplam Aktivite</h3>
                <div class="number" id="total">0</div>
            </div>
            <div class="card">
                <h3>Saldırı Tespit</h3>
                <div class="number" id="attacks">0</div>
            </div>
            <div class="card">
                <h3>Yüksek Risk</h3>
                <div class="number" id="highRisk">0</div>
            </div>
            <div class="card">
                <h3>Anlık Risk</h3>
                <div class="number" id="currentRisk">0%</div>
            </div>
        </div>
        
        <div class="risk-meter">
            <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                <span>Risk Seviyesi</span>
                <span class="live-badge">🔴 CANLI</span>
            </div>
            <div class="risk-bar">
                <div class="risk-fill" id="riskBar"></div>
            </div>
            <div style="display: flex; justify-content: space-between; color: #666; font-size: 12px;">
                <span>Düşük</span>
                <span>Orta</span>
                <span>Yüksek</span>
            </div>
        </div>
        
        <div class="activities">
            <h3 style="margin-bottom: 20px;">📊 Canlı Aktivite Akışı</h3>
            <div id="activityList"></div>
        </div>
        
        <div class="footer">
            AI Destekli Anomali Tespiti | Gerçek Zamanlı İzleme
        </div>
    </div>
    
    <script>
        function updateDashboard() {
            fetch('/api/data')
                .then(r => r.json())
                .then(data => {
                    document.getElementById('total').textContent = data.total;
                    document.getElementById('attacks').textContent = data.attacks;
                    document.getElementById('highRisk').textContent = data.high_risk;
                    
                    let riskPercent = (data.current_risk * 100).toFixed(1);
                    document.getElementById('currentRisk').textContent = riskPercent + '%';
                    document.getElementById('riskBar').style.width = riskPercent + '%';
                    
                    let html = '';
                    data.activities.forEach(act => {
                        let riskClass = act.risk > 0.7 ? 'risk-high' : (act.risk > 0.3 ? 'risk-medium' : 'risk-low');
                        html += `
                            <div class="activity ${act.risk > 0.7 ? 'high-risk' : ''}">
                                <div>
                                    <strong>${act.type}</strong>
                                    <div style="color: #666; font-size: 12px;">${act.location} • ${act.device}</div>
                                </div>
                                <div style="display: flex; align-items: center; gap: 15px;">
                                    <span class="risk-badge ${riskClass}">${(act.risk * 100).toFixed(0)}%</span>
                                    <span style="color: #666;">${act.time}</span>
                                </div>
                            </div>
                        `;
                    });
                    document.getElementById('activityList').innerHTML = html;
                });
        }
        
        setInterval(updateDashboard, 2000);
        updateDashboard();
    </script>
</body>
</html>
"""

# Veri üretimi
total = 0
attacks = 0
activities = []
current_risk = 0.3

def generate():
    global total, attacks, current_risk, activities
    
    types = ['Giriş', 'Playlist Oluşturma', 'Şarkı Dinleme', 'Beğeni', 'Paylaşım']
    locations = ['İstanbul', 'Ankara', 'İzmir', 'Sao Paulo', 'New York', 'London']
    devices = ['iPhone 15', 'MacBook Pro', 'Windows', 'Android', 'Linux']
    
    while True:
        time.sleep(2)
        
        # Risk hesapla
        risk = random.uniform(0, 1)
        if risk > 0.8:
            attacks += 1
            risk = random.uniform(0.7, 1.0)
        
        current_risk = current_risk * 0.7 + risk * 0.3
        
        activities.insert(0, {
            'type': random.choice(types),
            'location': random.choice(locations),
            'device': random.choice(devices),
            'risk': risk,
            'time': datetime.now().strftime('%H:%M:%S')
        })
        
        if len(activities) > 8:
            activities.pop()
        
        total += 1

threading.Thread(target=generate, daemon=True).start()

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/data')
def get_data():
    global total, attacks, current_risk, activities
    high = sum(1 for a in activities if a['risk'] > 0.7)
    return jsonify({
        'total': total,
        'attacks': attacks,
        'high_risk': high,
        'current_risk': current_risk,
        'activities': activities
    })

if __name__ == '__main__':
    print("""
    ╔════════════════════════════════════╗
    ║  🎵 Spotify Güvenlik Merkezi       ║
    ║  📍 http://localhost:5000          ║
    ║  🔄 Canlı güncelleme: 2 saniye    ║
    ╚════════════════════════════════════╝
    """)
    app.run(debug=True, port=5000)