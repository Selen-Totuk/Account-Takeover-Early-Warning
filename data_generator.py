# data_generator.py
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# --- 1. Rastgelelik için sabit değerler (Reproducibility için seed kullanıyoruz) ---
np.random.seed(42)
random.seed(42)

# --- 2. Kullanıcı Profillerini Tanımlama ---
# Normal kullanıcı: Selen
# Saldırgan: Bilinmiyor

# Olası lokasyonlar (enlem, boylam, ülke)
locations = {
    'istanbul': (41.0082, 28.9784, 'TR'),
    'ankara': (39.9334, 32.8597, 'TR'),
    'izmir': (38.4192, 27.1287, 'TR'),
    'sao_paulo': (-23.5505, -46.6333, 'BR'),
    'new_york': (40.7128, -74.0060, 'US'),
    'london': (51.5074, -0.1278, 'UK'),
    'berlin': (52.5200, 13.4050, 'DE'),
    'moscow': (55.7558, 37.6173, 'RU'),
}

# Cihaz türleri
devices = ['iPhone 13', 'iPhone 14', 'iPhone 15', 'Android (Samsung S23)', 'Android (Google Pixel 8)', 'Windows Laptop', 'MacBook Pro', 'Linux Desktop', 'iPad', 'Unknown Device']

# Müzik türleri
genres = ['pop', 'rock', 'jazz', 'classical', 'electronic', 'hip-hop', 'metal', 'reggae', 'folk', 'indie', 'k-pop', 'latin']

# Normal kullanıcının (Selen) tercih ettiği türler (daha yüksek olasılıkla seçilecek)
selen_fav_genres = ['pop', 'k-pop', 'indie', 'electronic']

# --- 3. Veri Üretme Fonksiyonu ---
def generate_user_activity(num_entries=1000, user_id='user_123', is_attacker=False):
    """
    Belirtilen sayıda kullanıcı aktivitesi üretir.
    Eğer is_attacker=True ise anormal davranışlar ekler.
    """
    activities = []
    start_time = datetime.now() - timedelta(days=30)  # 30 gün önceden başla

    for i in range(num_entries):
        # Varsayılan olarak normal kullanıcı profili
        current_time = start_time + timedelta(minutes=random.randint(0, 30*24*60))  # Rastgele zaman
        location = locations['istanbul']
        device = random.choice(['iPhone 13', 'iPhone 14', 'MacBook Pro'])
        genre = random.choice(selen_fav_genres + ['rock', 'jazz'])  # Ağırlıklı olarak sevilen türler
        playlist_created = 0
        playlist_modified = 0
        songs_played = random.randint(5, 25)
        songs_liked = random.randint(0, 5)

        # --- EĞER BU BİR SALDIRGANSA, DAVRANIŞLARI DEĞİŞTİR ---
        if is_attacker and i > num_entries * 0.7:  # Verinin son %30'luk kısmı saldırgan olsun (hesap ele geçirilmiş)
            # Saat dilimini değiştir: Gece vakti (Brezilya saatiyle 02:00-05:00 arası)
            attacker_hour = random.randint(2, 5)
            # Zamanı ayarla: Son günlerde, gece vakti
            current_time = datetime.now() - timedelta(days=random.randint(1, 3), hours=random.randint(0, 12))
            current_time = current_time.replace(hour=attacker_hour, minute=random.randint(0, 59))

            # Lokasyonu değiştir: Brezilya
            location = locations['sao_paulo']

            # Cihazı değiştir: Linux veya bilinmeyen cihaz
            device = random.choice(['Linux Desktop', 'Unknown Device'])

            # Müzik zevkini değiştir: Metal, rock, hip-hop gibi farklı türler
            genre = random.choice(['metal', 'hip-hop', 'reggae'])

            # Davranış değişikliği: Anomali yarat (çok fazla playlist oluşturma)
            playlist_created = random.randint(1, 5)  # Normalde hiç yapmazken, şimdi 5 tane yapıyor
            playlist_modified = random.randint(3, 10)
            songs_played = random.randint(1, 50)
            songs_liked = random.randint(5, 20)

        # Aktivite kaydını oluştur
        activity = {
            'timestamp': current_time,
            'user_id': user_id,
            'latitude': location[0],
            'longitude': location[1],
            'country': location[2],
            'device': device,
            'genre': genre,
            'playlist_created': playlist_created,
            'playlist_modified': playlist_modified,
            'songs_played': songs_played,
            'songs_liked': songs_liked,
            'is_attacker': is_attacker and i > num_entries * 0.7  # Etiketle (sadece son kısım)
        }
        activities.append(activity)

    return activities

# --- 4. Veriyi Üret ve Birleştir ---
print("🔵 Normal kullanıcı (Selen) verisi üretiliyor...")
normal_activities = generate_user_activity(num_entries=800, user_id='selen_01', is_attacker=False)

print("🔴 Saldırgan aktiviteleri üretiliyor (hesap ele geçirme simülasyonu)...")
attacker_activities = generate_user_activity(num_entries=200, user_id='selen_01', is_attacker=True)

# İki veri setini birleştir
all_activities = normal_activities + attacker_activities

# --- 5. DataFrame Oluştur ve Kaydet ---
df = pd.DataFrame(all_activities)

# Zaman damgasını indeks olarak ayarla (daha sonra zaman serisi analizi için faydalı)
df.sort_values(by='timestamp', inplace=True)
df.reset_index(drop=True, inplace=True)

# CSV olarak kaydet
df.to_csv('spotify_user_activity.csv', index=False)
print(f"✅ Veri başarıyla oluşturuldu! Toplam {len(df)} aktivite kaydı 'spotify_user_activity.csv' dosyasına kaydedildi.")
print(df.head(10))  # İlk 10 satırı göster