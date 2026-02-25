# spotify_guvenlik_dashboard.py
from flask import Flask, render_template_string, jsonify
import random
import threading
import time
from datetime import datetime

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Spotify Güvenlik Merkezi</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Circular', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #121212;
            color: #FFFFFF;
            line-height: 1.6;
            padding: 0;
        }
        
        /* Spotify Renkleri */
        :root {
            --spotify-green: #1DB954;
            --spotify-green-hover: #1ED760;
            --bg-base: #121212;
            --bg-highlight: #1A1A1A;
            --bg-card: #181818;
            --bg-card-hover: #282828;
            --text-primary: #FFFFFF;
            --text-secondary: #B3B3B3;
            --text-muted: #7A7A7A;
            --border: #2A2A2A;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }
        
        /* Header */
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
            padding: 20px 0;
            border-bottom: 1px solid var(--border);
        }
        
        .logo {
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .logo svg {
            width: 40px;
            height: 40px;
        }
        
        .logo h1 {
            font-size: 24px;
            font-weight: 700;
            background: linear-gradient(135deg, #FFFFFF, var(--spotify-green));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .live-badge {
            background: rgba(29, 185, 84, 0.1);
            color: var(--spotify-green);
            padding: 8px 16px;
            border-radius: 30px;
            font-size: 14px;
            font-weight: 600;
            border: 1px solid rgba(29, 185, 84, 0.3);
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.7; }
            100% { opacity: 1; }
        }
        
        /* İstatistik Kartları */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .stat-card {
            background: var(--bg-card);
            padding: 25px;
            border-radius: 12px;
            transition: all 0.3s;
            border: 1px solid transparent;
        }
        
        .stat-card:hover {
            background: var(--bg-card-hover);
            border-color: var(--spotify-green);
            transform: translateY(-2px);
        }
        
        .stat-label {
            font-size: 14px;
            color: var(--text-secondary);
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .stat-value {
            font-size: 42px;
            font-weight: 700;
            color: var(--text-primary);
            margin-bottom: 5px;
        }
        
        .stat-trend {
            font-size: 12px;
            color: var(--text-muted);
        }
        
        .trend-up { color: var(--spotify-green); }
        .trend-down { color: #F15E6C; }
        
        /* Risk Metre */
        .risk-section {
            background: var(--bg-card);
            padding: 25px;
            border-radius: 12px;
            margin-bottom: 30px;
        }
        
        .risk-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        
        .risk-header h3 {
            font-size: 16px;
            font-weight: 600;
            color: var(--text-secondary);
        }
        
        .risk-percentage {
            font-size: 28px;
            font-weight: 700;
            color: var(--spotify-green);
        }
        
        .risk-bar-container {
            height: 8px;
            background: var(--bg-highlight);
            border-radius: 4px;
            overflow: hidden;
            margin-bottom: 10px;
        }
        
        .risk-bar-fill {
            height: 100%;
            width: 0%;
            background: linear-gradient(90deg, var(--spotify-green), #FFD700, #F15E6C);
            transition: width 0.5s ease;
        }
        
        .risk-labels {
            display: flex;
            justify-content: space-between;
            font-size: 12px;
            color: var(--text-muted);
        }
        
        /* İçerik Grid */
        .content-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 25px;
            margin-bottom: 30px;
        }
        
        .panel {
            background: var(--bg-card);
            border-radius: 12px;
            padding: 20px;
        }
        
        .panel-title {
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid var(--border);
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .panel-title span {
            color: var(--spotify-green);
        }
        
        /* Timeline */
        .timeline {
            max-height: 400px;
            overflow-y: auto;
        }
        
        .timeline-item {
            display: flex;
            align-items: center;
            padding: 12px 0;
            border-bottom: 1px solid var(--border);
        }
        
        .timeline-dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-right: 15px;
        }
        
        .dot-green { background: var(--spotify-green); }
        .dot-yellow { background: #FFD700; }
        .dot-red { background: #F15E6C; }
        
        .timeline-content {
            flex: 1;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .timeline-time {
            color: var(--text-muted);
            font-size: 13px;
        }
        
        /* Live Stream */
        .live-stream {
            max-height: 400px;
            overflow-y: auto;
        }
        
        .event-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px 0;
            border-bottom: 1px solid var(--border);
            animation: slideIn 0.3s;
        }
        
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateX(-20px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }
        
        .event-info {
            flex: 1;
        }
        
        .event-type {
            font-weight: 600;
            margin-bottom: 5px;
        }
        
        .event-meta {
            font-size: 12px;
            color: var(--text-muted);
            display: flex;
            gap: 15px;
        }
        
        .event-risk {
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
        }
        
        .risk-low {
            background: rgba(29, 185, 84, 0.2);
            color: var(--spotify-green);
        }
        
        .risk-medium {
            background: rgba(255, 215, 0, 0.2);
            color: #FFD700;
        }
        
        .risk-high {
            background: rgba(241, 94, 108, 0.2);
            color: #F15E6C;
        }
        
        /* Footer */
        .footer {
            text-align: center;
            padding: 30px 0 20px;
            color: var(--text-muted);
            font-size: 13px;
            border-top: 1px solid var(--border);
        }
        
        .footer span {
            color: var(--spotify-green);
        }
        
        /* Scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: var(--bg-highlight);
        }
        
        ::-webkit-scrollbar-thumb {
            background: var(--border);
            border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: var(--spotify-green);
        }
        
        /* Responsive */
        @media (max-width: 900px) {
            .stats-grid {
                grid-template-columns: repeat(2, 1fr);
            }
            .content-grid {
                grid-template-columns: 1fr;
            }
        }
        
        @media (max-width: 500px) {
            .stats-grid {
                grid-template-columns: 1fr;
            }
            .header {
                flex-direction: column;
                gap: 15px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <div class="logo">
                <svg viewBox="0 0 24 24" fill="#1DB954">
                    <circle cx="12" cy="12" r="10"/>
                    <path d="M8 12L10 14L16 8" stroke="white" stroke-width="2" fill="none"/>
                </svg>
                <h1>Spotify Güvenlik Merkezi</h1>
            </div>
            <div class="live-badge">🔴 CANLI İZLEME</div>
        </div>
        
        <!-- İstatistikler -->
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">Toplam Aktivite</div>
                <div class="stat-value" id="totalCount">0</div>
                <div class="stat-trend trend-up">↑ %12 bu hafta</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Şüpheli İşlem</div>
                <div class="stat-value" id="suspiciousCount">0</div>
                <div class="stat-trend trend-down">↓ %5 geçen hafta</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Yüksek Risk</div>
                <div class="stat-value" id="highRiskCount">0</div>
                <div class="stat-trend trend-up">↑ %8 son 24 saat</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Risk Oranı</div>
                <div class="stat-value" id="riskPercentage">0%</div>
                <div class="stat-trend">toplam aktivite</div>
            </div>
        </div>
        
        <!-- Risk Metre -->
        <div class="risk-section">
            <div class="risk-header">
                <h3>ANLIK RİSK SEVİYESİ</h3>
                <span class="risk-percentage" id="currentRiskValue">%0</span>
            </div>
            <div class="risk-bar-container">
                <div class="risk-bar-fill" id="riskBar"></div>
            </div>
            <div class="risk-labels">
                <span>GÜVENLİ</span>
                <span>DÜŞÜK</span>
                <span>ORTA</span>
                <span>YÜKSEK</span>
                <span>KRİTİK</span>
            </div>
        </div>
        
        <!-- Ana Grid -->
        <div class="content-grid">
            <!-- Zaman Çizelgesi -->
            <div class="panel">
                <div class="panel-title">
                    <span>📊</span> Zaman Çizelgesi
                </div>
                <div class="timeline" id="timeline">
                    <!-- JS ile doldurulacak -->
                </div>
            </div>
            
            <!-- Canlı Akış -->
            <div class="panel">
                <div class="panel-title">
                    <span>⚡</span> Canlı Olay Akışı
                </div>
                <div class="live-stream" id="liveEvents">
                    <!-- JS ile doldurulacak -->
                </div>
            </div>
        </div>
        
        <!-- Footer -->
        <div class="footer">
            <span>Spotify</span> • Hesap Güvenliği Erken Uyarı Sistemi • AI Destekli Anomali Tespiti
        </div>
    </div>
    
    <script>
        function updateDashboard() {
            fetch('/api/veri')
                .then(response => response.json())
                .then(data => {
                    // İstatistikleri güncelle
                    document.getElementById('totalCount').textContent = data.toplam;
                    document.getElementById('suspiciousCount').textContent = data.supheli;
                    document.getElementById('highRiskCount').textContent = data.yuksek_risk;
                    
                    // Risk yüzdesi
                    let riskYuzde = data.toplam > 0 ? ((data.supheli / data.toplam) * 100).toFixed(1) : '0.0';
                    document.getElementById('riskPercentage').textContent = riskYuzde + '%';
                    
                    // Anlık risk
                    let anlikRisk = (data.anlik_risk * 100).toFixed(1);
                    document.getElementById('currentRiskValue').textContent = '%' + anlikRisk;
                    document.getElementById('riskBar').style.width = anlikRisk + '%';
                    
                    // Timeline
                    let timelineHtml = '';
                    data.zaman_cizelgesi.forEach(olay => {
                        let renk = 'dot-green';
                        if (olay.risk > 0.7) renk = 'dot-red';
                        else if (olay.risk > 0.3) renk = 'dot-yellow';
                        
                        timelineHtml += `
                            <div class="timeline-item">
                                <div class="timeline-dot ${renk}"></div>
                                <div class="timeline-content">
                                    <span>${olay.tip}</span>
                                    <span class="timeline-time">${olay.zaman}</span>
                                </div>
                            </div>
                        `;
                    });
                    document.getElementById('timeline').innerHTML = timelineHtml;
                    
                    // Canlı olaylar
                    let eventsHtml = '';
                    data.canli_olaylar.forEach(olay => {
                        let riskClass = 'risk-low';
                        if (olay.risk > 0.7) riskClass = 'risk-high';
                        else if (olay.risk > 0.3) riskClass = 'risk-medium';
                        
                        eventsHtml += `
                            <div class="event-item">
                                <div class="event-info">
                                    <div class="event-type">${olay.tip}</div>
                                    <div class="event-meta">
                                        <span>📍 ${olay.konum}</span>
                                        <span>📱 ${olay.cihaz}</span>
                                    </div>
                                </div>
                                <div>
                                    <span class="event-risk ${riskClass}">${Math.round(olay.risk * 100)}%</span>
                                    <span style="color: #7A7A7A; font-size: 11px; margin-left: 10px;">${olay.zaman}</span>
                                </div>
                            </div>
                        `;
                    });
                    document.getElementById('liveEvents').innerHTML = eventsHtml;
                });
        }
        
        // İlk yükleme
        updateDashboard();
        
        // Her 3 saniyede güncelle
        setInterval(updateDashboard, 3000);
    </script>
</body>
</html>
"""

# ============================================
# VERİ ÜRETİMİ
# ============================================

toplam = 0
supheli = 0
anlik_risk = 0.15
olaylar = []

tipler = [
    "🎵 Şarkı Dinleme",
    "🔐 Giriş Yapma",
    "📝 Playlist Oluşturma",
    "❤️ Şarkı Beğenme",
    "🔄 Paylaşım Yapma",
    "⚠️ Başarısız Giriş"
]

konumlar_normal = ["İstanbul", "Ankara", "İzmir", "Bursa", "Antalya"]
konumlar_supheli = ["Sao Paulo", "Moskova", "Pekin", "Lagos", "Bilinmeyen"]
cihazlar_normal = ["iPhone 15", "MacBook Pro", "iPad", "Windows PC"]
cihazlar_supheli = ["Linux", "Unknown Device", "Android Emulator"]

def yeni_olay():
    global toplam, supheli, anlik_risk, olaylar
    
    # Rastgele olay
    supheli_mi = random.random() < 0.10  # %10 şüpheli
    
    if supheli_mi:
        risk = random.uniform(0.65, 0.95)
        supheli += 1
        konum = random.choice(konumlar_supheli)
        cihaz = random.choice(cihazlar_supheli)
    else:
        risk = random.uniform(0.05, 0.30)
        konum = random.choice(konumlar_normal)
        cihaz = random.choice(cihazlar_normal)
    
    # Anlık risk güncelle (hareketli ortalama)
    anlik_risk = anlik_risk * 0.7 + risk * 0.3
    
    # Olay oluştur
    olay = {
        "tip": random.choice(tipler),
        "konum": konum,
        "cihaz": cihaz,
        "risk": risk,
        "zaman": datetime.now().strftime("%H:%M:%S")
    }
    
    olaylar.insert(0, olay)
    if len(olaylar) > 20:
        olaylar.pop()
    
    toplam += 1

# Arka plan çalışanı
def arkaplan():
    while True:
        yeni_olay()
        time.sleep(random.uniform(2, 4))

threading.Thread(target=arkaplan, daemon=True).start()

# ============================================
# API
# ============================================

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/veri')
def veri():
    yuksek = sum(1 for o in olaylar if o["risk"] > 0.7)
    
    # Zaman çizelgesi için son 8 olay
    zaman = []
    for o in olaylar[:8]:
        zaman.append({
            "tip": o["tip"],
            "zaman": o["zaman"],
            "risk": o["risk"]
        })
    
    return jsonify({
        "toplam": toplam,
        "supheli": supheli,
        "yuksek_risk": yuksek,
        "anlik_risk": anlik_risk,
        "zaman_cizelgesi": zaman,
        "canli_olaylar": olaylar[:12]
    })

# ============================================
# BAŞLAT
# ============================================

if __name__ == '__main__':
    print("""
    ╔════════════════════════════════════════════════╗
    ║     🎵 SPOTIFY GÜVENLİK MERKEZİ                ║
    ║                                                ║
    ║  📍 http://localhost:5000                      ║
    ║  🔄 Gerçek zamanlı izleme                      ║
    ║  🤖 AI Destekli Anomali Tespiti                ║
    ╚════════════════════════════════════════════════╝
    """)
    app.run(debug=False, port=5000)