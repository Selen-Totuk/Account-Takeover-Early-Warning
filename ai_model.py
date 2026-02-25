# ai_model.py
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
import joblib

def train_isolation_forest(df):
    """
    Isolation Forest ile anomali tespiti yapar
    """
    print("🤖 Isolation Forest modeli eğitiliyor...")
    
    # Model için kullanılacak özellikler
    feature_cols = [
        'hour', 'is_night', 'is_weekend',
        'songs_played', 'playlist_created', 'playlist_modified', 'songs_liked',
        'avg_songs_played', 'avg_playlist_created', 'avg_songs_liked',
        'songs_played_zscore', 'playlist_created_zscore',
        'distance_km', 'speed_kmh', 'country_changed', 'impossible_travel',
        'is_new_device', 'genre_changed', 'genre_rarity'
    ]
    
    # Özelliklerin var olduğundan emin ol
    available_features = [col for col in feature_cols if col in df.columns]
    print(f"📊 Kullanılacak özellik sayısı: {len(available_features)}")
    
    # Veriyi hazırla
    X = df[available_features].copy()
    
    # NaN değerleri temizle
    X = X.fillna(0)
    
    # Ölçeklendir (Isolation Forest için önemli değil ama genel olarak iyi pratik)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Modeli eğit
    model = IsolationForest(
        contamination=0.1,  # Verinin %10'unun anomali olmasını bekliyoruz
        random_state=42,
        n_estimators=100,
        max_samples='auto',
        bootstrap=False
    )
    
    model.fit(X_scaled)
    
    # Tahmin yap
    # Isolation Forest: 1 = normal, -1 = anomali
    predictions = model.predict(X_scaled)
    
    # Anomali skorları (düşük skor = daha anormal)
    anomaly_scores = model.score_samples(X_scaled)
    
    # Skorları 0-1 arası normalize et (1 = yüksek risk)
    min_score = anomaly_scores.min()
    max_score = anomaly_scores.max()
    normalized_scores = 1 - (anomaly_scores - min_score) / (max_score - min_score)
    
    return model, scaler, predictions, normalized_scores, available_features

def evaluate_model(df, predictions, anomaly_scores):
    """
    Model performansını değerlendirir
    """
    print("\n📊 Model Değerlendirmesi:")
    print("="*50)
    
    # Gerçek etiketler var mı?
    if 'is_attacker' in df.columns:
        # Isolation Forest çıktısını düzenle (-1 anomali, 1 normal) -> (1 anomali, 0 normal)
        y_true = df['is_attacker'].astype(int)
        y_pred = (predictions == -1).astype(int)
        
        print("\n🔍 Karmaşıklık Matrisi:")
        cm = confusion_matrix(y_true, y_pred)
        print(cm)
        
        print("\n📈 Sınıflandırma Raporu:")
        print(classification_report(y_true, y_pred, target_names=['Normal', 'Saldırı']))
        
        # Gerçek saldırıları yakalama oranı
        attack_detection_rate = cm[1,1] / (cm[1,0] + cm[1,1]) if (cm[1,0] + cm[1,1]) > 0 else 0
        print(f"🎯 Saldırı Yakalama Oranı: {attack_detection_rate:.2%}")
        
        # False positive rate
        false_positive_rate = cm[0,1] / (cm[0,0] + cm[0,1]) if (cm[0,0] + cm[0,1]) > 0 else 0
        print(f"⚠️  False Positive Oranı: {false_positive_rate:.2%}")
    
    # Anomali skor istatistikleri
    print("\n📊 Anomali Skor İstatistikleri:")
    print(f"Ortalama anomali skoru: {anomaly_scores.mean():.3f}")
    print(f"Maksimum anomali skoru: {anomaly_scores.max():.3f}")
    print(f"Minimum anomali skoru: {anomaly_scores.min():.3f}")
    print(f"Anomali tespit edilen aktivite sayısı: {(predictions == -1).sum()}")

def plot_results(df, predictions, anomaly_scores):
    """
    Sonuçları görselleştirir
    """
    print("\n📈 Grafikler oluşturuluyor...")
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    
    # 1. Zaman serisi - Risk skoru vs Anomali skoru
    ax1 = axes[0, 0]
    if 'timestamp' in df.columns:
        time_data = pd.to_datetime(df['timestamp'])
        ax1.scatter(time_data, df['risk_score'], alpha=0.5, label='Kural Bazlı Risk', s=10)
        ax1.scatter(time_data, anomaly_scores, alpha=0.5, label='AI Anomali Skoru', s=10)
        
        # Saldırıları işaretle
        if 'is_attacker' in df.columns:
            attack_idx = df[df['is_attacker'] == True].index
            ax1.scatter(time_data.iloc[attack_idx], df.loc[attack_idx, 'risk_score'], 
                       color='red', s=50, marker='X', label='Gerçek Saldırı')
        
        ax1.set_xlabel('Zaman')
        ax1.set_ylabel('Skor')
        ax1.set_title('Zaman İçinde Risk ve Anomali Skorları')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
    
    # 2. Anomali skoru dağılımı
    ax2 = axes[0, 1]
    ax2.hist(anomaly_scores, bins=30, alpha=0.7, edgecolor='black')
    ax2.axvline(x=anomaly_scores.mean(), color='red', linestyle='--', label=f'Ortalama: {anomaly_scores.mean():.2f}')
    ax2.set_xlabel('Anomali Skoru')
    ax2.set_ylabel('Frekans')
    ax2.set_title('Anomali Skorları Dağılımı')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 3. Özellik önemleri (basit korelasyon)
    ax3 = axes[1, 0]
    if 'is_attacker' in df.columns:
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        correlations = df[numeric_cols].corrwith(df['is_attacker']).abs().sort_values(ascending=False).head(10)
        correlations.plot(kind='barh', ax=ax3)
        ax3.set_xlabel('Korelasyon (mutlak)')
        ax3.set_title('Saldırı ile En İlişkili Özellikler')
        ax3.grid(True, alpha=0.3)
    
    # 4. Risk skoru vs Anomali skoru
    ax4 = axes[1, 1]
    ax4.scatter(df['risk_score'], anomaly_scores, alpha=0.5, c=predictions, cmap='coolwarm')
    ax4.set_xlabel('Kural Bazlı Risk Skoru')
    ax4.set_ylabel('AI Anomali Skoru')
    ax4.set_title('Risk Skoru vs Anomali Skoru')
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('model_analysis.png', dpi=150, bbox_inches='tight')
    plt.show()
    print("💾 Grafik 'model_analysis.png' olarak kaydedildi.")

if __name__ == "__main__":
    # Veriyi yükle
    print("📂 Veri yükleniyor...")
    df = pd.read_csv('spotify_features.csv')
    print(f"Yüklenen veri boyutu: {df.shape}")
    
    # Modeli eğit
    model, scaler, predictions, anomaly_scores, features = train_isolation_forest(df)
    
    # Değerlendir
    evaluate_model(df, predictions, anomaly_scores)
    
    # Görselleştir
    plot_results(df, predictions, anomaly_scores)
    
    # Modeli kaydet
    joblib.dump(model, 'isolation_forest_model.pkl')
    joblib.dump(scaler, 'scaler.pkl')
    print("\n💾 Model 'isolation_forest_model.pkl' olarak kaydedildi.")
    
    # Yüksek riskli aktiviteleri listele
    high_risk = (predictions == -1)
    print(f"\n🚨 Yüksek riskli tespit edilen {high_risk.sum()} aktivite:")
    high_risk_df = df[high_risk][['timestamp', 'hour', 'device', 'country', 'genre', 
                                   'risk_score']].copy()
    high_risk_df['anomaly_score'] = anomaly_scores[high_risk]
    print(high_risk_df.to_string(index=False))