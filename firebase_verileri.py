import firebase_admin
from firebase_admin import credentials, firestore
import os

# JSON dosyasının bulunduğu dizini otomatik bul
json_path = os.path.join(os.path.dirname(__file__), "egitimuygulamasi-6a5d7-firebase-adminsdk-fbsvc-2c98e81232.json")

# Firebase bağlantısını başlat (ilk kez başlatılmamışsa)
if not firebase_admin._apps:
    cred = credentials.Certificate(json_path)
    firebase_admin.initialize_app(cred)

# Firestore istemcisi
db = firestore.client()

# Firestore'dan verileri çeken fonksiyon
def verileri_cek():
    hedefler_ref = db.collection('hedefler')
    docs = hedefler_ref.stream()

    grouped_data = {}

    for doc in docs:
        data = doc.to_dict()
        grup = data.get('grup', '').strip()
        ders = data.get('ders', '').strip()

        if not grup or not ders:
            continue

        if grup not in grouped_data:
            grouped_data[grup] = {}

        grouped_data[grup][ders] = {
            "KISA VADELİ HEDEFLER": data.get('kisa_vadeli_hedefler', []),
            "UZUN VADELİ HEDEFLER": data.get('uzun_vadeli_hedefler', []),
            "ÖĞRETİMSEL HEDEFLER": data.get('ogretimsel_hedefler', [])
        }

    return grouped_data
