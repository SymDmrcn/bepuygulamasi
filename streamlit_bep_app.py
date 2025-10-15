import json
import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from docx import Document

firebase_config = st.secrets["firebase_config"]
cred = credentials.Certificate(dict(firebase_config))
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)
db = firestore.client()

# Cache'e TTL ekle (5 dakikada bir yenilenir)
@st.cache_data(ttl=30)  
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
            "KISA VADELİ HEDEFLER": data.get("kısa_vadeli_hedefler", []),
            "UZUN VADELİ HEDEFLER": data.get("uzun_vadeli_hedefler", []),
            "ÖĞRETİMSEL HEDEFLER": data.get("ogretimsel_hedefler", [])
        }
    
    return grouped_data

# 🎨 Arayüz
st.set_page_config(page_title="BEP Oluşturucu", layout="centered")
st.title("📘 TUZLA BİLSEM Bireyselleştirilmiş Eğitim Planı Otomasyonu (BEP)")

# Cache temizleme butonu ekle (geliştirme aşamasında kullanışlı)
if st.sidebar.button("🔄 Verileri Yenile"):
    st.cache_data.clear()
    st.rerun()

grouped_data = verileri_cek()

teacher = st.text_input("👩‍🏫 Öğretmen Adı")
student = st.text_input("👧 Öğrenci Adı")

if grouped_data:
    group = st.selectbox("🎯 Grup Seçin", list(grouped_data.keys()))
    lesson = st.selectbox("📚 Ders Seçin", list(grouped_data[group].keys()))
    
    hedefler = grouped_data[group][lesson]
    
    short_selected = st.multiselect("📝 Kısa Vadeli Hedefler", hedefler["KISA VADELİ HEDEFLER"])
    long_selected = st.multiselect("🧭 Uzun Vadeli Hedefler", hedefler["UZUN VADELİ HEDEFLER"])
    teach_selected = st.multiselect("📖 Öğretimsel Hedefler", hedefler["ÖĞRETİMSEL HEDEFLER"])
    
    if st.button("📄 Word Belgesi Oluştur"):
        if not teacher or not student:
            st.error("Lütfen öğretmen ve öğrenci adlarını giriniz.")
        else:
            doc = Document()
            doc.add_heading("Bireyselleştirilmiş Eğitim Planı", level=1)
            doc.add_paragraph(f"Öğretmen: {teacher}")
            doc.add_paragraph(f"Öğrenci: {student}")
            doc.add_paragraph(f"Grup: {group}")
            doc.add_paragraph(f"Ders: {lesson}")
            
            if short_selected:
                doc.add_heading("Kısa Vadeli Hedefler", level=2)
                for item in short_selected:
                    doc.add_paragraph(f"- {item}")
                    
            if long_selected:
                doc.add_heading("Uzun Vadeli Hedefler", level=2)
                for item in long_selected:
                    doc.add_paragraph(f"- {item}")
                    
            if teach_selected:
                doc.add_heading("Öğretimsel Hedefler", level=2)
                for item in teach_selected:
                    doc.add_paragraph(f"- {item}")
            
            file_name = f"{student.replace(' ', '_')}_bep.docx"
            doc.save(file_name)
            
            with open(file_name, "rb") as f:
                st.download_button("📥 Word Belgesini İndir", f, file_name=file_name)
else:
    st.warning("Henüz Firestore'dan veri alınamadı.")
