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

# Cache'e TTL ekle (5 saniyede bir yenilenir - geliştirme için)
@st.cache_data(ttl=5)
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
        
        # Kısa vadeli hedefleri birleştir
        kisa_vadeli = []
        kisa_vadeli.extend(data.get("kisa_vadeli_hedefler", []))
        kisa_vadeli.extend(data.get("kısa_vadeli_hedefler", []))
        
        # Uzun vadeli hedefleri birleştir
        uzun_vadeli = []
        uzun_vadeli.extend(data.get("uzun_vadeli_hedefler", []))
        uzun_vadeli.extend(data.get("uzak_vadeli_hedefler", []))
        
        # Öğretimsel hedefleri birleştir  
        ogretimsel = []
        ogretimsel.extend(data.get("ogretimsel_hedefler", []))
        ogretimsel.extend(data.get("öğretimsel_hedefler", []))
        
        grouped_data[grup][ders] = {
            "KISA_VADELI_HEDEFLER": list(set(kisa_vadeli)),  # Dublicateleri kaldır
            "UZUN_VADELI_HEDEFLER": list(set(uzun_vadeli)),  # Dublicateleri kaldır
            "OGRETIMSEL_HEDEFLER": list(set(ogretimsel))  # Dublicateleri kaldır
        }
    
    return grouped_data

# 🎨 Arayüz
st.set_page_config(page_title="BEP Oluşturucu", layout="centered")
st.title("📘 TUZLA BİLSEM Bireyselleştirilmiş Eğitim Planı Otomasyonu (BEP)")

# Cache temizleme butonu
if st.sidebar.button("🔄 Verileri Yenile"):
    st.cache_data.clear()
    st.rerun()

# Debug bilgileri (geliştirme aşamasında)
if st.sidebar.checkbox("🔍 Debug Modu"):
    st.sidebar.write("**Cache Durumu:**")
    st.sidebar.write(f"Cache TTL: 30 saniye")
    
grouped_data = verileri_cek()

# Debug modu aktifse verileri göster
if st.sidebar.checkbox("🔍 Debug Modu"):
    st.sidebar.write("**Bulunan Gruplar:**")
    for grup in grouped_data.keys():
        st.sidebar.write(f"- {grup}")
        for ders in grouped_data[grup].keys():
            st.sidebar.write(f"  └─ {ders}")

teacher = st.text_input("👩‍🏫 Öğretmen Adı")
student = st.text_input("👧 Öğrenci Adı")

if grouped_data:
    group = st.selectbox("🎯 Grup Seçin", list(grouped_data.keys()))
    lesson = st.selectbox("📚 Ders Seçin", list(grouped_data[group].keys()))
    
    hedefler = grouped_data[group][lesson]
    
    # Düzeltilmiş multiselect'ler
    short_selected = st.multiselect("📝 Kısa Vadeli Hedefler", hedefler["KISA_VADELI_HEDEFLER"])
    long_selected = st.multiselect("🧭 Uzun Vadeli Hedefler", hedefler["UZUN_VADELI_HEDEFLER"])
    teach_selected = st.multiselect("📖 Öğretimsel Hedefler", hedefler["OGRETIMSEL_HEDEFLER"])
    
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
