import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
import json
from docx import Document

# Firebase kimliği doğrudan kod içinde
firebase_config = {
  "type": "service_account",
  "project_id": "egitimuygulamasi-6a5d7",
  "private_key_id": "2c98e81232b4e84d32ccdabccf7b7d058a0f05c8",
  "private_key": """-----BEGIN PRIVATE KEY-----
MIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQDh+i7XUY0r9V3D
6S89MTXrQqvh2Q4j55x/Ri+uoA4xw6UALmBkI6RYaQa0eJ0yyRTVojIbxcW1ipk7
sqqWwWPtuQRCmZwbaZTxw7e7R7X/xJsFyJ/DOWVSGZfG0nCKaOqjs7DT85CKcWuS
tmxvanxAZa9L5+ioEbh7ltCklgs/7v7P4330kgmv5B7V2xDg9XQZ4O9JeOxtbVbf
1cjw2uJqdMu8sXOObGmWFjAzMEewC2GEZ2cS0tcHxxZQGcWgg6S2146sb/odxkRD
bAQ3lnqpwbY/M1FORCvk2QWPPEwKOmhv70yiPoW4IQzQvNwH5vUaTXeHwrehPyaC
ZwBD4TYHAgMBAAECggEAPxw+/rVw5sj08eTq430d4OFS3ZVgBJkHtOfmIy/iJvXL
3BwXoX/uwx452CcjR+6umedddTIrwEK//tMsH0RNYzPbw7ngxisbhNWzN2OUqaS/
4sKgE8awzFgHcmiNM6qPdT6W8OrCAFgiweuepxMnNljvtxRCfsXMLv/0rzKUW7se
J1R5Yj1Xto8PLebFmJ15VmFqN+br1VRkjvY3ZbDp3Cq0Z7uAGC3SLiVsOF+Sqy+y
H3fmOqtGqvlQj6ac3HTUOfK1O+nCpMvefxehR33rlKPwSabc7IoXt0ygYRymAonS
gTIgnFNwk1rgUTweIo6uXcmkwkQHMDMRWtK9nuE8aQKBgQDyZ06tCl2SzAKixuln
r90JB6C1ATNMXEh00IgUVDF5muG3xo3tQpvOdJWTyuk6PTfnqWOTMZz/LhPU0IJ5
CgYFS4+iKqK9DM4cIteVQqE7LkUF5fq7C4xs2LgNsxE7OcO+k9HUN7U1o+8rfCa4
hofpBRqikWDnK1Z4oTGoekvQjQKBgQDupwJvOKH0HXtF3DNdI+elos7FxJzLaJJ/
vePAKpTMl2VOI+7L/ysjKq7qgym8VB64dULFuyxXaAQT9Ts7JTdUYhQdQZo8Jjxv
pGdHZoq1rUI9NxAvYdoi3ZN0WJSJzB2xaZUhRa42GCWTj/ffhSoNZ62vISSElEGy
gshEj5it4wKBgF+I0ZwnOqvRVbSbmn+v8vhNFkxgFbyhnjjTut3wNLONlCoeye7Z
UpiyoATocrTuTasyujjX091KZqx4JQPZLHhHyGsMTKkfc9fo73g3E15EpRVnB0NS
kNyRKTDVAxSJdpkUnxz5e6SRYICN5KDS/Juc1Ft/2mYhUWondW/GCz09AoGAWf3+
TAR2BcCsQH61m7SzYGFRSYBHg+iN/b+UR12HONMKL3obTS+Oi7dHuET3kv3Bi9sj
774SDW+6we/igv4YrChD33hiebYNaif7jhAb1EBeTwkZgFSM1kLpnKDeekvPEpx2
0NIezGU0nj1WwiHL5rwm4XhE9f2V/IOWk0v2zfMCgYA0OmfhXKKQr9KOv9SsoiUd
wlJHYz4YkrHXvNQjSEeXRXq5wpOKmlRr3I/VLmzuQPBTUnSTO/aa8pP0fEiEC1r8
eGgYDoenzadqz9PCwWfE1ZsrA2mWvXYSot+XLC8kTLOnMxYLxrSfd2XCNCJ1ObIv
aDb6oGGGm0J3Xv+5w5WZdg==
-----END PRIVATE KEY-----""",
  "client_email": "firebase-adminsdk-fbsvc@egitimuygulamasi-6a5d7.iam.gserviceaccount.com",
  "client_id": "113481276794026592826",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc@egitimuygulamasi-6a5d7.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}

if not firebase_admin._apps:
    cred = credentials.Certificate(firebase_config)
    firebase_admin.initialize_app(cred)

db = firestore.client()

# Devamında kodun aynı şekilde devam edebilir (verileri_cek, arayüz, butonlar vs.)
