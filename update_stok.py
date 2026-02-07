import requests
from bs4 import BeautifulSoup
import os

Link Produk Spesifik Kamu
URL_PRODUK = "https://www.itemku.com/dagangan/mobile-legends-akun-smurf-sultan-bp-64k-gratis-pilih-1-hero-ryujin-gage/1038381"
WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK')

def cek_stok():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(URL_PRODUK, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

Mencari teks stok di halaman produk
Itemku sering menggunakan tag span atau div untuk angka stok
        stok_label = soup.find(text=lambda t: "Stok" in t)

        if stok_label:
            pesan = f"📦 Update Stok Itemku!\nProduk: Akun Smurf Sultan\nStatus: {stok_label.strip()}\nLink: {URL_PRODUK}"
            requests.post(WEBHOOK_URL, json={"content": pesan})
            print("Berhasil kirim ke Discord")
        else:
            print("Elemen stok tidak ditemukan, mungkin struktur web berubah.")
    except Exception as e:
        print(f"Error: {e}")

if name == "main":
    cek_stok()
