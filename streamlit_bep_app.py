import json
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from docx import Document

# 🔐 Firebase kimliğini Streamlit secrets üzerinden al
firebase_json = json.loads(st.secrets["firebase_config"])
cred = credentials.Certificate(firebase_json)

if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

db = firestore.client()


# Firestore'dan verileri çekme
@st.cache_data
def verileri_cek():
    hedefler_ref = db.collection('hedefler')
    docs = hedefler_ref.stream()

    grouped_data = {}
    for doc in docs:
        data = doc.to_dict()
        grup = data.get("grup", "").strip()
        ders = data.get("ders", "").strip()
        if not grup or not ders:
            continue
        if grup not in grouped_data:
            grouped_data[grup] = {}
        grouped_data[grup][ders] = {
            "KISA VADELİ HEDEFLER": data.get("kisa_vadeli_hedefler", []),
            "UZUN VADELİ HEDEFLER": data.get("uzun_vadeli_hedefler", []),
            "ÖĞRETİMSEL HEDEFLER": data.get("ogretimsel_hedefler", [])
        }
    return grouped_data

# Arayüz ayarları
st.set_page_config(page_title="BEP Hedefleri", layout="centered")
st.title("📘 Bireyselleştirilmiş Eğitim Planı Oluşturucu")

# Firebase'den verileri çek
grouped_data = verileri_cek()

# Kullanıcı girişi
teacher = st.text_input("Öğretmen Adı")
student = st.text_input("Öğrenci Adı")

group = st.selectbox("Grup Seçin", list(grouped_data.keys()))
lesson = st.selectbox("Ders Seçin", list(grouped_data[group].keys()))

hedefler = grouped_data[group][lesson]

short_selected = st.multiselect("Kısa Vadeli Hedefler", hedefler["KISA VADELİ HEDEFLER"])
long_selected = st.multiselect("Uzun Vadeli Hedefler", hedefler["UZUN VADELİ HEDEFLER"])
teach_selected = st.multiselect("Öğretimsel Hedefler", hedefler["ÖĞRETİMSEL HEDEFLER"])

# Word çıktısı oluştur ve indir
if st.button("Word Belgesi Oluştur"):
    if not teacher or not student:
        st.error("Lütfen öğretmen ve öğrenci adlarını girin.")
    else:
        doc = Document()
        doc.add_heading("Bireyselleştirilmiş Eğitim Planı", level=1)
        doc.add_paragraph(f"Öğretmen Adı: {teacher}")
        doc.add_paragraph(f"Öğrenci Adı: {student}")
        doc.add_paragraph(f"Grup: {group}")
        doc.add_paragraph(f"Ders: {lesson}")

        if short_selected:
            doc.add_heading("Kısa Vadeli Hedefler", level=2)
            for hedef in short_selected:
                doc.add_paragraph(f"- {hedef}")
        if long_selected:
            doc.add_heading("Uzun Vadeli Hedefler", level=2)
            for hedef in long_selected:
                doc.add_paragraph(f"- {hedef}")
        if teach_selected:
            doc.add_heading("Öğretimsel Hedefler", level=2)
            for hedef in teach_selected:
                doc.add_paragraph(f"- {hedef}")

        file_name = f"{student.replace(' ', '_')}_bep.docx"
        doc.save(file_name)

        with open(file_name, "rb") as f:
            st.download_button("📥 Word Dosyasını İndir", f, file_name=file_name)
