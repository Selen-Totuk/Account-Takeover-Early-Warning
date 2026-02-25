# app.py
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import pandas as pd
import numpy as np
import joblib
from datetime import datetime, timedelta
import plotly
import plotly.graph_objs as go
import plotly.express as px
import json
import random
from threading import Thread
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'spotify-security-secret'
socketio = SocketIO(app, cors_allowed_origins="*")

# Model ve verileri yükle
print("📂 Model ve veriler yükleniyor...")
try:
    model = joblib.load('isolation_forest_model.pkl')
    scaler = joblib.load('scaler.pkl')
    df = pd.read_csv('spotify_features.csv')
    print("✅ Yükleme başarılı!")
except:
    print("⚠️  Model bulunamadı, örnek veri oluşturuluyor...")
    # Örnek veri oluştur
    np.random.seed(42)
    df = pd.DataFrame({
        'timestamp': pd.date_range(start='2026-01-01', periods=100, freq='H'),
        'risk_score': np.random.uniform(0, 1, 100),
        'anomaly_score': np.random.uniform(0, 1, 100),
        'device': np.random.choice(['iPhone', 'Android', 'MacBook', 'Windows'], 100),
        'country': np.random.choice(['TR', 'US', 'BR', 'UK'], 100),
        'is_attacker': np.random.choice([0, 1], 100, p=[0.9, 0.1])
    })

# Canlı veri simülasyonu için
live_data = []
current_risk = 0.5

def generate_live_activity():
    """Canlı aktivite üret"""
    activities = [
        {
            'type': 'Giriş',
            'location': np.random.choice(['İstanbul', 'Ankara', 'İzmir', 'Sao Paulo', 'New York']),
            'device': np.random.choice(['iPhone 15', 'MacBook Pro', 'Linux Desktop', 'Unknown Device']),
            'time': datetime.now().strftime('%H:%M:%S'),
            'risk': np.random.uniform(0, 1)
        },
        {
            'type': 'Playlist Oluşturma',
            'count': np.random.randint(1, 10),
            'genre': np.random.choice(['Pop', 'Rock', 'Metal', 'K-Pop', 'Jazz']),
            'time': datetime.now().strftime('%H:%M:%S'),
            'risk': np.random.uniform(0, 1)
        },
        {
            'type': 'Şarkı Dinleme',
            'count': np.random.randint(5, 50),
            'device': np.random.choice(['iPhone', 'MacBook', 'Windows']),
            'time': datetime.now().strftime('%H:%M:%S'),
            'risk': np.random.uniform(0, 1)
        }
    ]
    return random.choice(activities)

def background_thread():
    """Arka planda canlı veri üret"""
    global live_data, current_risk
    while True:
        time.sleep(3)  # 3 saniyede bir güncelle
        activity = generate_live_activity()
        current_risk = activity['risk']
        live_data.append(activity)
        if len(live_data) > 20:  # Son 20 aktiviteyi tut
            live_data.pop(0)
        
        # Socket ile frontend'e gönder
        socketio.emit('new_activity', {
            'activity': activity,
            'risk': current_risk,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/api/stats')
def get_stats():
    """İstatistikleri döndür"""
    total_activities = len(df)
    attacks = df['is_attacker'].sum() if 'is_attacker' in df.columns else 0
    high_risk = (df['risk_score'] > 0.7).sum() if 'risk_score' in df.columns else 0
    
    return jsonify({
        'total_activities': int(total_activities),
        'attacks': int(attacks),
        'high_risk': int(high_risk),
        'current_risk': float(current_risk),
        'attack_rate': float(attacks / total_activities * 100) if total_activities > 0 else 0
    })

@app.route('/api/risk-timeline')
def risk_timeline():
    """Risk zaman çizelgesi grafiği"""
    if 'timestamp' in df.columns and 'risk_score' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        fig = go.Figure()
        
        # Risk skoru
        fig.add_trace(go.Scatter(
            x=df['timestamp'].tail(50),
            y=df['risk_score'].tail(50),
            mode='lines+markers',
            name='Risk Skoru',
            line=dict(color='orange', width=2),
            marker=dict(size=4)
        ))
        
        # Saldırı anları
        if 'is_attacker' in df.columns:
            attacks = df[df['is_attacker'] == True].tail(50)
            if len(attacks) > 0:
                fig.add_trace(go.Scatter(
                    x=attacks['timestamp'],
                    y=attacks['risk_score'],
                    mode='markers',
                    name='Saldırı',
                    marker=dict(color='red', size=10, symbol='x')
                ))
        
        fig.update_layout(
            title='Son 50 Aktivite - Risk Skoru',
            xaxis_title='Zaman',
            yaxis_title='Risk Skoru',
            template='plotly_dark',
            hovermode='x'
        )
        
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return jsonify({})

@app.route('/api/devices')
def device_distribution():
    """Cihaz dağılımı"""
    if 'device' in df.columns:
        device_counts = df['device'].value_counts()
        
        fig = go.Figure(data=[go.Pie(
            labels=device_counts.index,
            values=device_counts.values,
            hole=0.4,
            marker=dict(colors=px.colors.qualitative.Set3)
        )])
        
        fig.update_layout(
            title='Cihaz Dağılımı',
            template='plotly_dark'
        )
        
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return jsonify({})

@app.route('/api/locations')
def location_map():
    """Lokasyon haritası"""
    if 'latitude' in df.columns and 'longitude' in df.columns:
        fig = go.Figure()
        
        fig.add_trace(go.Scattergeo(
            lon=df['longitude'],
            lat=df['latitude'],
            mode='markers',
            marker=dict(
                size=df['risk_score'] * 20,
                color=df['risk_score'],
                colorscale='RdYlGn_r',
                showscale=True,
                colorbar=dict(title="Risk Skoru")
            ),
            text=df['country'],
            hoverinfo='text+lon+lat'
        ))
        
        fig.update_layout(
            title='Aktivitelerin Lokasyonları',
            geo=dict(
                projection_type='natural earth',
                showland=True,
                landcolor='rgb(243, 243, 243)',
                countrycolor='rgb(204, 204, 204)'
            ),
            template='plotly_dark'
        )
        
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return jsonify({})

@app.route('/api/live-activities')
def get_live_activities():
    """Son canlı aktiviteler"""
    return jsonify(live_data[-10:])  # Son 10 aktivite

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('connected', {'data': 'Connected to server'})
    # Arka plan iş parçacığını başlat
    thread = Thread(target=background_thread)
    thread.daemon = True
    thread.start()

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000)