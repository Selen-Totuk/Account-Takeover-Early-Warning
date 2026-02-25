# feature_engineering.py (düzeltilmiş versiyon)
import pandas as pd
import numpy as np
from datetime import datetime
import math

def calculate_distance(lat1, lon1, lat2, lon2):
    """Haversine formülü ile iki nokta arası mesafe (km)"""
    R = 6371  # Dünya yarıçapı (km)
    
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    return R * c

def engineer_features(df):
    """
    Ham veriden anlamlı özellikler çıkarır
    """
    print("🚀 Özellik mühendisliği başlıyor...")
    
    # Kopya oluştur
    data = df.copy()
    
    # Zaman sütununu datetime'a çevir
    data['timestamp'] = pd.to_datetime(data['timestamp'])
    data = data.sort_values('timestamp').reset_index(drop=True)
    
    # 1. ZAMAN BAZLI ÖZELLİKLER
    print("⏰ Zaman bazlı özellikler çıkarılıyor...")
    data['hour'] = data['timestamp'].dt.hour
    data['day_of_week'] = data['timestamp'].dt.dayofweek
    data['is_weekend'] = data['day_of_week'].isin([5, 6]).astype(int)
    data['is_night'] = ((data['hour'] >= 23) | (data['hour'] <= 5)).astype(int)
    
    # 2. LOKASYON BAZLI ÖZELLİKLER
    print("📍 Lokasyon bazlı özellikler çıkarılıyor...")
    
    # Bir önceki lokasyonla karşılaştır
    data['prev_latitude'] = data['latitude'].shift(1)
    data['prev_longitude'] = data['longitude'].shift(1)
    data['prev_timestamp'] = data['timestamp'].shift(1)
    data['prev_country'] = data['country'].shift(1)
    
    # Mesafe ve hız hesapla
    distances = []
    speeds = []
    country_changes = []
    impossible_travels = []
    
    for i in range(len(data)):
        if i == 0 or pd.isna(data.loc[i, 'prev_latitude']):
            distances.append(0)
            speeds.append(0)
            country_changes.append(0)
            impossible_travels.append(0)
            continue
            
        # Mesafe hesapla
        distance = calculate_distance(
            data.loc[i, 'prev_latitude'], data.loc[i, 'prev_longitude'],
            data.loc[i, 'latitude'], data.loc[i, 'longitude']
        )
        distances.append(distance)
        
        # Zaman farkı (saat)
        time_diff = (data.loc[i, 'timestamp'] - data.loc[i, 'prev_timestamp']).total_seconds() / 3600
        
        # Hız (km/saat)
        speed = distance / time_diff if time_diff > 0 else 0
        speeds.append(speed)
        
        # Ülke değişikliği
        country_change = 1 if data.loc[i, 'prev_country'] != data.loc[i, 'country'] else 0
        country_changes.append(country_change)
        
        # Impossible Travel (10 dakikada 1000km'den fazla imkansız)
        time_diff_min = time_diff * 60  # dakika cinsinden
        impossible_travel = 1 if (time_diff_min < 10 and distance > 1000) else 0
        impossible_travels.append(impossible_travel)
    
    data['distance_km'] = distances
    data['speed_kmh'] = speeds
    data['country_changed'] = country_changes
    data['impossible_travel'] = impossible_travels
    
    # 3. CİHAZ BAZLI ÖZELLİKLER
    print("📱 Cihaz bazlı özellikler çıkarılıyor...")
    
    # Daha önce görülen cihazlar
    seen_devices = []
    is_new_device = []
    
    for device in data['device']:
        if device not in seen_devices:
            is_new_device.append(1)
            seen_devices.append(device)
        else:
            is_new_device.append(0)
    
    data['is_new_device'] = is_new_device
    data['device_entropy'] = len(set(data['device']))  # Toplam benzersiz cihaz sayısı
    
    # 4. DAVRANIŞ BAZLI ÖZELLİKLER (sayısal)
    print("🎵 Davranış bazlı özellikler çıkarılıyor...")
    
    window = 10
    
    # Sayısal sütunlar için rolling hesaplamalar
    numeric_cols = ['songs_played', 'playlist_created', 'playlist_modified', 'songs_liked']
    
    for col in numeric_cols:
        # Hareketli ortalama
        data[f'avg_{col}'] = data[col].rolling(window=window, min_periods=1).mean()
        
        # Hareketli standart sapma
        data[f'std_{col}'] = data[col].rolling(window=window, min_periods=1).std().fillna(0)
        
        # Z-score (anomali skoru)
        data[f'{col}_zscore'] = (data[col] - data[f'avg_{col}']) / data[f'std_{col}'].replace(0, 1)
    
    # 5. MÜZİK ZEVKİ DEĞİŞİMİ (kategorik)
    print("🔄 Müzik zevki analizi yapılıyor...")
    
    # Her kullanıcı için tipik türleri hesapla
    user_genre_stats = {}
    
    genre_changed = []
    genre_rarity = []
    
    for i in range(len(data)):
        user = data.loc[i, 'user_id']
        current_genre = data.loc[i, 'genre']
        
        # Kullanıcının geçmiş türlerini topla
        if user not in user_genre_stats:
            user_genre_stats[user] = {'genres': [], 'total': 0}
        
        # Tür değişikliği kontrolü
        if len(user_genre_stats[user]['genres']) > 0:
            prev_genre = user_genre_stats[user]['genres'][-1]
            changed = 1 if prev_genre != current_genre else 0
            genre_changed.append(changed)
        else:
            genre_changed.append(0)
        
        # Tür nadirliği (bu tür daha önce kaç kez görüldü?)
        genre_count = user_genre_stats[user]['genres'].count(current_genre)
        total = len(user_genre_stats[user]['genres']) + 1
        rarity = 1 - (genre_count / total) if total > 0 else 0
        genre_rarity.append(rarity)
        
        # Güncelle
        user_genre_stats[user]['genres'].append(current_genre)
    
    data['genre_changed'] = genre_changed
    data['genre_rarity'] = genre_rarity
    
    # 6. RİSK SKORU BİLEŞENLERİ
    print("📊 Risk bileşenleri hesaplanıyor...")
    
    # Her bir anomali için risk puanı
    risk_components = pd.DataFrame()
    
    # Impossible Travel riski
    risk_components['location_risk'] = data['impossible_travel'] * 0.3
    
    # Yeni cihaz riski
    risk_components['device_risk'] = data['is_new_device'] * 0.2
    
    # Gece aktivitesi riski
    risk_components['night_risk'] = data['is_night'] * 0.15
    
    # Ülke değişikliği riski
    risk_components['country_risk'] = data['country_changed'] * 0.2
    
    # Anomali riski (yüksek z-score)
    risk_components['anomaly_risk'] = (
        (np.abs(data['songs_played_zscore']) > 2) | 
        (np.abs(data['playlist_created_zscore']) > 2)
    ).astype(float) * 0.15
    
    # Tür nadirliği riski
    risk_components['genre_risk'] = data['genre_rarity'] * 0.1
    
    # Toplam risk skoru (0-1 arası)
    data['risk_score'] = risk_components.sum(axis=1)
    
    # Risk skorunu normalize et (0-1 arası)
    if data['risk_score'].max() > data['risk_score'].min():
        data['risk_score'] = (data['risk_score'] - data['risk_score'].min()) / (data['risk_score'].max() - data['risk_score'].min())
    
    # 7. TEMİZLİK
    print("🧹 Gereksiz sütunlar temizleniyor...")
    columns_to_drop = ['prev_latitude', 'prev_longitude', 'prev_timestamp', 'prev_country']
    
    data = data.drop(columns=[col for col in columns_to_drop if col in data.columns])
    
    print("✅ Özellik mühendisliği tamamlandı!")
    print(f"📈 Toplam özellik sayısı: {len(data.columns)}")
    
    return data

if __name__ == "__main__":
    # Veriyi yükle
    print("📂 Veri yükleniyor...")
    df = pd.read_csv('spotify_user_activity.csv')
    print(f"Yüklenen veri boyutu: {df.shape}")
    
    # Özellik mühendisliği uygula
    featured_df = engineer_features(df)
    
    # Sonuçları kaydet
    featured_df.to_csv('spotify_features.csv', index=False)
    print(f"💾 Özellikler 'spotify_features.csv' dosyasına kaydedildi.")
    
    # İstatistikler
    print("\n📊 Risk Skoru İstatistikleri:")
    print(f"Ortalama risk: {featured_df['risk_score'].mean():.3f}")
    print(f"Maksimum risk: {featured_df['risk_score'].max():.3f}")
    print(f"Minimum risk: {featured_df['risk_score'].min():.3f}")
    print(f"Yüksek riskli (>0.7) aktivite sayısı: {(featured_df['risk_score'] > 0.7).sum()}")
    
    # İlk 10 satırı göster
    print("\n📋 İlk 10 aktivite:")
    print(featured_df[['timestamp', 'hour', 'device', 'genre', 'country_changed', 'impossible_travel', 'is_new_device', 'risk_score']].head(10))
    
    # Gerçek saldırıları ne kadar iyi tahmin ettiğimize bakalım
    if 'is_attacker' in featured_df.columns:
        high_risk_attacks = featured_df[(featured_df['risk_score'] > 0.7) & (featured_df['is_attacker'] == True)].shape[0]
        total_attacks = featured_df[featured_df['is_attacker'] == True].shape[0]
        if total_attacks > 0:
            print(f"\n🎯 Yüksek riskli aktivitelerin saldırı yakalama oranı: {high_risk_attacks}/{total_attacks} ({(high_risk_attacks/total_attacks)*100:.1f}%)")