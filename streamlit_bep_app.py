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

# Cache'e TTL ekle (30 saniyede bir yenilenir)
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
        
        # Her iki Türkçe karakter versiyonunu da kontrol et
        kisa_vadeli = data.get("kisa_vadeli_hedefler", []) or data.get("kısa_vadeli_hedefler", [])
        uzun_vadeli = data.get("uzun_vadeli_hedefler", [])
        ogretimsel = data.get("ogretimsel_hedefler", []) or data.get("öğretimsel_hedefler", [])
        
        grouped_data[grup][ders] = {
            "KISA VADELİ HEDEFLER": kisa_vadeli,
            "UZUN VADELİ HEDEFLER": uzun_vadeli,
            "ÖĞRETİMSEL HEDEFLER": ogretimsel
        }
    
    return grouped_data

# 🎨 Arayüz
st.set_page_config(page_title="BEP Oluşturucu", layout="centered")
st.title("📘 TUZLA BİLSEM Bireyselleştirilmiş Eğitim Planı Otomasyonu (BEP)")

# Cache temizleme butonu ekle
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

# ============================================
# 🎵 ADMIN: MÜZİK GRUPLARI EKLEME
# ============================================
st.sidebar.markdown("---")
st.sidebar.header("🎵 Admin: Müzik Grupları")

if st.sidebar.button("ÖYG 3, 4 VE PROJE EKLE"):
    muzik_gruplari = {
        "ÖYG 3": {
            "kisa": [
                "Bir eğitim yılı sonunda öğrencinin müzik kuramı, işitme, ses eğitimi ve müzik kültürü alanlarında temel bilgi ve becerilerini geliştirmesi",
                "Bireysel ve grup çalışmalarıyla müziksel ifade becerilerini uygulamaya dönüştürmesi",
                "Beste, doğaçlama, performans ve temsil çalışmalarında özgün yorumlar ortaya koyması",
                "Türk müzik kültürünü, müzik türlerini ve bestecileri tanıması",
                "Müzik kurum ve kuruluşlarının işlevlerini ve toplumsal rollerini kavraması",
                "Müzik etkinliklerinde aktif katılım sağlayarak sahne disiplini, sorumluluk bilinci ve estetik duyarlılık göstermesi"
            ],
            "uzun": [
                "Öğrencinin müzik alanındaki bilgi, beceri ve estetik birikimini geliştirerek müziği bir ifade aracı olarak kullanabilen birey hâline gelmesi",
                "Yaratıcı düşünebilen, analitik düşünebilen, işbirliği yapabilen ve performans becerilerini sergileyebilen birey hâline gelmesi"
            ],
            "ogretimsel": [
                "Akor türlerini ve çevrimlerini tanır",
                "Tonal dizileri (majör, minör, modlar vb.) ayırt eder",
                "Müzik biçimlerini (motif, cümle, dönem, bölüm) tanımlar",
                "Akor kurma ve çözümleme becerisi geliştirir",
                "İşitsel analiz yaparak akorları ve tonal merkezleri ayırt eder",
                "Notaları doğru intonasyonla seslendirir",
                "Müzikal ifadeyi dinleyerek değerlendirir",
                "Ses ve nefes egzersizlerini doğru teknikle uygular",
                "Eserleri notalarına uygun şekilde seslendirir",
                "Şarkı, marş ve türküleri doğru sürelerle ve ifadeyle söyler",
                "Duygularını müzik yoluyla doğaçlama olarak ifade eder",
                "Basit ritmik ya da melodik motifler besteler",
                "Müziksel üretim sürecinde özgün fikirler geliştirir",
                "Türk müziği, popüler müzik ve klasik müzik türlerini ayırt eder",
                "Türk bestecilerini ve müziğe katkılarını açıklar",
                "Farklı müzik türleri arasında benzerlik ve farklılıkları tartışır",
                "Sahne konumu ve kullanımına ilişkin bilgi ve beceri gösterir",
                "Performanslarını bireysel ve toplu çalışmalarda sergiler",
                "Koro veya orkestra içinde uyumlu biçimde çalar/söyler",
                "Performansını eleştirel biçimde değerlendirir",
                "Müzik kurum ve kuruluşlarını tanır",
                "Kurumlarda gerçekleşen müzik etkinliklerini gözlemler",
                "Etkinliklerden elde ettiği bilgileri raporlaştırır",
                "Kurumların müzik kültürüne katkılarını değerlendirir"
            ]
        },
        "ÖYG 4": {
            "kisa": [
                "Bir eğitim yılı sonunda temel müzik kuramlarını (dizi, aralık, akor, tonalite) uygulamalı olarak kullanabilmesi",
                "Farklı tür ve dönemlerdeki eserleri seslendirme ve analiz edebilmesi",
                "Türk müziği makam ve usullerini tanıyıp uygulayabilmesi",
                "Müzik teknolojilerini etkin biçimde kullanarak performans ve kayıt yapabilmesi",
                "Toplu ve bireysel müzik çalışmaları yoluyla müzikal ifade gücü ve özgüvenini artırması",
                "Estetik duyarlılığını ve müzik kültürünü geliştirmesi"
            ],
            "uzun": [
                "Öğrencinin müzik alanında kuramsal bilgi, işitsel algı, yorumlama ve üretim becerilerini geliştirerek müziği bilinçli, estetik ve yaratıcı biçimde ifade edebilen birey hâline gelmesi"
            ],
            "ogretimsel": [
                "Do, Sol, Re Majör dizilerini doğru perde ilişkileriyle seslendirir",
                "Tonalite ve akor bağlaşımı kurallarına uygun kısa melodik cümleler yazar",
                "Majör ve minör tonal alanlarda temel kadansları tanır ve uygular",
                "Şarkı söylerken nefes, artikülasyon ve entonasyon kontrolünü sağlar",
                "Türk müziğinde temel makamları (Rast, Hüseyni, Nihavent vb.) tanır ve örnek eserlerle uygular",
                "Usul vuruşlarını (9/8, 10/8, 4/4 vb.) doğru şekilde uygular",
                "Müzik biçimlerini (şarkı formu, rondo, ikili form) tanır ve örneklerle ilişkilendirir",
                "Dönemsel müzik tarzlarını (Barok, Klasik, Romantik, Çağdaş) karşılaştırır",
                "Müzik yazılımı veya dijital kayıt araçlarını kullanarak kısa bir çalışma üretir",
                "Toplu müzik çalışmalarında işbirliği ve müzikal uyum becerisi gösterir",
                "Dinlediği eserleri biçim, dizi, ritim ve tını yönlerinden analiz eder",
                "Müzikal performansını sahne disiplini içinde sergiler"
            ]
        },
        "PROJE": {
            "kisa": [
                "Bir eğitim yılı sonunda müzik alanında bir araştırma konusu belirleyip proje planı oluşturması",
                "Proje sürecinde müzik kuramı, teknoloji ve yaratıcılığı bütünleştirmesi",
                "Müzikal üretiminde (beste, düzenleme, analiz, performans, sunum vb.) özgün bir yaklaşım geliştirmesi",
                "Proje çıktısını etkili biçimde sunması ve değerlendirmesi",
                "Bireysel sorumluluk ve grup çalışması becerilerini sergilemesi",
                "Sanatsal düşünme, eleştirel sorgulama ve estetik duyarlılığını geliştirmesi"
            ],
            "uzun": [
                "Öğrencinin müzik alanındaki bilgi, beceri ve estetik birikimini kullanarak özgün, araştırmaya dayalı, yaratıcı ve disiplinlerarası müzik projeleri geliştiren bir birey hâline gelmesi"
            ],
            "ogretimsel": [
                "Proje sürecinde bir müzik araştırma konusu belirler ve amacını açıklar",
                "Proje planı, yöntem ve takvimini oluşturur",
                "Veri toplama, kaynak tarama ve analiz aşamalarını yürütür",
                "Müzik kuramı bilgilerini proje içeriğinde uygular",
                "Beste, düzenleme, analiz, ses tasarımı veya performans yoluyla özgün bir müzikal ürün ortaya koyar",
                "Müzik teknolojilerini (DAW, nota yazım, ses kayıt yazılımları vb.) etkin biçimde kullanır",
                "Proje sürecini raporlaştırır (amaç, yöntem, bulgular, değerlendirme bölümleriyle)",
                "Proje çıktısını (performans, kayıt, sunum, rapor vb.) uygun ortamda paylaşır",
                "Akran değerlendirmesi yapar ve geribildirimleri dikkate alır",
                "Eleştirel düşünme becerisiyle kendi çalışmasını değerlendirir",
                "Disiplinlerarası bağlantılar kurarak müzikle diğer alanları ilişkilendirir",
                "Etkili iletişim, işbirliği ve estetik ifade becerisi gösterir"
            ]
        }
    }
    
    sayac = 0
    for grup_adi, hedefler in muzik_gruplari.items():
        doc_ref = db.collection('hedefler').document()
        hedef_data = {
            'ders': 'MÜZİK',
            'grup': grup_adi,
            'kisa_vadeli_hedefler': hedefler['kisa'],
            'uzun_vadeli_hedefler': hedefler['uzun'],
            'ogretimsel_hedefler': hedefler['ogretimsel']
        }
        doc_ref.set(hedef_data)
        sayac += 1
    
    st.sidebar.success(f"✅ {sayac} grup (ÖYG 3, 4 ve PROJE) eklendi! Şimdi 'Verileri Yenile' butonuna bas.")
