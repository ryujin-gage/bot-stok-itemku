import requests
from bs4 import BeautifulSoup
import os

Link Produk Kamu
URL_PRODUK = "https://www.itemku.com/dagangan/mobile-legends-akun-smurf-sultan-bp-64k-gratis-pilih-1-hero-ryujin-gage/1038381"
WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK')

def cek_stok():
    # Header lebih lengkap agar dikira Browser Chrome asli
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
        "Referer": "https://www.google.com/"
    }

    try:
        print(f"Mencoba akses: {URL_PRODUK}")
        response = requests.get(URL_PRODUK, headers=headers, timeout=15)

        if response.status_code != 200:
            print(f"Gagal akses web! Status Code: {response.status_code}")
            return

        soup = BeautifulSoup(response.text, 'html.parser')

Cara baru: Mencari teks angka stok yang biasanya ada di dekat tulisan 'Stok'
Kita ambil teks mentah dulu untuk pengecekan
        html_text = soup.get_text()

        if "Stok" in html_text:
            # Mencoba kirim potongan teks yang ada kata 'Stok'-nya ke Discord
            start_index = html_text.find("Stok")
            info_stok = html_text[start_index:start_index+20].strip()

            pesan = {
                "embeds": [{
                    "title": "📦 Update Stok Itemku",
                    "description": f"Status: {info_stok}\n[Klik Lihat Produk]({URL_PRODUK})",
                    "color": 5814783
                }]
            }
            requests.post(WEBHOOK_URL, json=pesan)
            print("Berhasil kirim laporan ke Discord!")
        else:
            print("Teks 'Stok' tidak ditemukan di halaman.")

    except Exception as e:
        print(f"Terjadi error: {e}")

if name == "main":
    cek_stok()
