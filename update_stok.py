import requests
from bs4 import BeautifulSoup
import os

# Link Produk Spesifik Kamu
URL_PRODUK = "https://www.itemku.com/dagangan/mobile-legends-akun-smurf-sultan-bp-64k-gratis-pilih-1-hero-ryujin-gage/1038381"
WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK')

def cek_stok():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(URL_PRODUK, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Mencari teks yang mengandung kata 'Stok'
        stok_label = soup.find(text=lambda t: "Stok" in t)
        
        if stok_label:
            info_stok = stok_label.strip()
            pesan = {
                "embeds": [{
                    "title": "📦 Update Stok Itemku",
                    "description": f"**Status:** {info_stok}\n[Klik Lihat Produk]({URL_PRODUK})",
                    "color": 5814783
                }]
            }
            requests.post(WEBHOOK_URL, json=pesan)
            print("Berhasil kirim ke Discord")
        else:
            print("Teks stok tidak ditemukan")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    cek_stok()
