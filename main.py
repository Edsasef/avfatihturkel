import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from supabase import create_client, Client
from dotenv import load_dotenv

# .env dosyasındaki değişkenleri yükle
load_dotenv()

app = FastAPI(title="Avukat İletişim API")

# CORS ayarları
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Supabase Bağlantısı
supabase_url: str = os.environ.get("SUPABASE_URL")
supabase_key: str = os.environ.get("SUPABASE_KEY")

if not supabase_url or not supabase_key:
    raise ValueError("Supabase kimlik bilgileri eksik.")

supabase: Client = create_client(supabase_url, supabase_key)

class IletisimFormu(BaseModel):
    ad_soyad: str
    eposta: EmailStr
    telefon: str = None
    hukuki_alan: str
    mesaj: str

# Mail gönderme fonksiyonu (Sana ve Kullanıcıya)
def mail_gonder(form: IletisimFormu):
    gonderici_email = os.environ.get("EMAIL_USER")
    gonderici_sifre = os.environ.get("EMAIL_PASSWORD")
    alici_email = "avfatihturkel@gmail.com"

    if not gonderici_email or not gonderici_sifre:
        print("Mail gönderimi başarısız: .env bilgileri eksik.")
        return

    # ---------------------------------------------------------
    # 1. BİZE GELECEK BİLDİRİM MAİLİ (Sana)
    # ---------------------------------------------------------
    mesaj_admin = MIMEMultipart("alternative")
    mesaj_admin["From"] = f"Web Sitesi <{gonderici_email}>"
    mesaj_admin["To"] = alici_email
    mesaj_admin["Subject"] = f"Yeni Danışmanlık Talebi: {form.ad_soyad}"

    html_admin = f"""
    <!DOCTYPE html>
    <html>
    <body style="font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; background-color: #f4f4f4; padding: 20px; margin: 0;">
        <table width="100%" border="0" cellspacing="0" cellpadding="0" style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.05);">
            <tr>
                <td style="background-color: #2A1B12; padding: 30px 20px; text-align: center; border-bottom: 4px solid #D4AF37;">
                    <h1 style="color: #D4AF37; margin: 0; font-size: 22px; font-weight: bold; letter-spacing: 1px;">
                        <span style="color: #ffffff;">AV.</span> ALPARSLAN FATİH TÜRKEL
                    </h1>
                    <p style="color: #a3a3a3; margin: 5px 0 0 0; font-size: 11px; letter-spacing: 2px;">HUKUK & DANIŞMANLIK</p>
                </td>
            </tr>
            <tr>
                <td style="padding: 40px 30px;">
                    <h2 style="color: #2A1B12; font-size: 18px; margin-top: 0; margin-bottom: 20px; border-bottom: 1px solid #eeeeee; padding-bottom: 10px;">
                        Web Sitenizden Yeni Bir Talep Geldi
                    </h2>
                    <table width="100%" border="0" cellspacing="0" cellpadding="0" style="font-size: 14px;">
                        <tr><td style="padding: 12px 0; border-bottom: 1px solid #f5f5f5; width: 140px; font-weight: bold; color: #4A3525;">Ad Soyad:</td>
                            <td style="padding: 12px 0; border-bottom: 1px solid #f5f5f5; color: #333333;">{form.ad_soyad}</td></tr>
                        <tr><td style="padding: 12px 0; border-bottom: 1px solid #f5f5f5; font-weight: bold; color: #4A3525;">E-Posta:</td>
                            <td style="padding: 12px 0; border-bottom: 1px solid #f5f5f5;"><a href="mailto:{form.eposta}" style="color: #D4AF37; text-decoration: none; font-weight: bold;">{form.eposta}</a></td></tr>
                        <tr><td style="padding: 12px 0; border-bottom: 1px solid #f5f5f5; font-weight: bold; color: #4A3525;">Telefon:</td>
                            <td style="padding: 12px 0; border-bottom: 1px solid #f5f5f5; color: #333333;">{form.telefon if form.telefon else '<i style="color:#999;">Belirtilmedi</i>'}</td></tr>
                        <tr><td style="padding: 12px 0; font-weight: bold; color: #4A3525;">Danışmanlık Alanı:</td>
                            <td style="padding: 12px 0; color: #333333;"><span style="background-color: #F3E5AB; color: #2A1B12; padding: 4px 10px; border-radius: 4px; font-size: 12px; font-weight: bold;">{form.hukuki_alan}</span></td></tr>
                    </table>
                    <h3 style="font-size: 14px; color: #4A3525; margin-top: 30px; margin-bottom: 10px;">Müvekkil Mesajı:</h3>
                    <div style="background-color: #fafafa; padding: 15px 20px; border-left: 4px solid #D4AF37; color: #555555; line-height: 1.6; font-size: 14px; border-radius: 0 4px 4px 0;">{form.mesaj}</div>
                </td>
            </tr>
            <tr>
                <td style="background-color: #f9f9f9; padding: 20px; text-align: center; font-size: 12px; color: #888888; border-top: 1px solid #eeeeee;">
                    Bu e-posta, <strong>avukatfatihturkel.com</strong> iletişim formu aracılığıyla otomatik gönderilmiştir.
                </td>
            </tr>
        </table>
    </body>
    </html>
    """
    mesaj_admin.attach(MIMEText(html_admin, "html", "utf-8"))


    # ---------------------------------------------------------
    # 2. KULLANICIYA GİDECEK OTOMATİK TEŞEKKÜR MAİLİ (Müvekkile)
    # ---------------------------------------------------------
    mesaj_kullanici = MIMEMultipart("alternative")
    mesaj_kullanici["From"] = f"Av. Alparslan Fatih Türkel <{gonderici_email}>"
    mesaj_kullanici["To"] = form.eposta
    mesaj_kullanici["Subject"] = "Talebiniz Alınmıştır - Av. Alparslan Fatih Türkel Hukuk & Danışmanlık"

    html_kullanici = f"""
    <!DOCTYPE html>
    <html>
    <body style="font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; background-color: #f4f4f4; padding: 20px; margin: 0;">
        <table width="100%" border="0" cellspacing="0" cellpadding="0" style="max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 15px rgba(0,0,0,0.05);">
            <tr>
                <td style="background-color: #2A1B12; padding: 30px 20px; text-align: center; border-bottom: 4px solid #D4AF37;">
                    <h1 style="color: #D4AF37; margin: 0; font-size: 22px; font-weight: bold; letter-spacing: 1px;">
                        <span style="color: #ffffff;">AV.</span> ALPARSLAN FATİH TÜRKEL
                    </h1>
                    <p style="color: #a3a3a3; margin: 5px 0 0 0; font-size: 11px; letter-spacing: 2px;">HUKUK & DANIŞMANLIK</p>
                </td>
            </tr>
            <tr>
                <td style="padding: 40px 30px;">
                    <h2 style="color: #2A1B12; font-size: 20px; margin-top: 0; margin-bottom: 20px;">
                        Sayın {form.ad_soyad},
                    </h2>
                    <p style="color: #555555; line-height: 1.6; font-size: 15px; margin-bottom: 20px;">
                        Hukuki danışmanlık talebiniz tarafımıza başarıyla ulaşmıştır. Göstermiş olduğunuz ilgi ve güven için teşekkür ederiz.
                    </p>
                    <p style="color: #555555; line-height: 1.6; font-size: 15px; margin-bottom: 30px;">
                        İletmiş olduğunuz bilgiler uzman ekibimiz tarafından incelemeye alınmış olup, değerlendirme sonrasında belirlediğiniz iletişim kanalları üzerinden en kısa sürede tarafınıza dönüş sağlanacaktır.
                    </p>
                    <div style="background-color: #fafafa; padding: 15px 20px; border-left: 4px solid #D4AF37; font-size: 13px; color: #666666; border-radius: 0 4px 4px 0;">
                        <strong>Özet Talep Bilgileriniz:</strong><br><br>
                        <strong>Konu:</strong> {form.hukuki_alan}<br>
                        <strong>İletişim:</strong> {form.telefon if form.telefon else form.eposta}
                    </div>
                </td>
            </tr>
            <tr>
                <td style="background-color: #f9f9f9; padding: 20px; text-align: center; font-size: 12px; color: #888888; border-top: 1px solid #eeeeee;">
                    Bu e-posta otomatik olarak oluşturulmuştur. Lütfen yanıtlamayınız.<br>
                    Acil durumlar için doğrudan web sitemizdeki telefon numaralarından bize ulaşabilirsiniz.
                </td>
            </tr>
        </table>
    </body>
    </html>
    """
    mesaj_kullanici.attach(MIMEText(html_kullanici, "html", "utf-8"))

    # Sunucuya bağlanıp her iki maili de tek seferde gönderiyoruz
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(gonderici_email, gonderici_sifre)
        
        # 1. Admin maili gönder
        server.send_message(mesaj_admin)
        # 2. Kullanıcı teşekkür maili gönder
        server.send_message(mesaj_kullanici)
        
        server.quit()
    except Exception as e:
        print(f"Mail gönderme hatası: {str(e)}")

# İletişim endpoint'i (Arka plan işlemi aktif)
@app.post("/api/iletisim")
async def iletisim_mesaji_gonder(form: IletisimFormu, background_tasks: BackgroundTasks):
    try:
        # 1. Veriyi Supabase'e kaydet
        supabase.table("iletisim_mesajlari").insert({
            "ad_soyad": form.ad_soyad,
            "eposta": form.eposta,
            "telefon": form.telefon,
            "hukuki_alan": form.hukuki_alan,
            "mesaj": form.mesaj
        }).execute()
        
        # 2. Arka planda mailleri gönder
        background_tasks.add_task(mail_gonder, form)
        
        return {"mesaj": "Talebiniz başarıyla alındı. En kısa sürede dönüş yapılacaktır.", "durum": "basarili"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bir hata oluştu: {str(e)}")

@app.get("/")
async def root():
    return {"mesaj": "Avukat API Sistemine Hoş Geldiniz. Sistem Aktif."}