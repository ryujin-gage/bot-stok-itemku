import cloudscraper
from bs4 import BeautifulSoup
import os

# Konfigurasi
URL_PRODUK = "https://www.itemku.com/dagangan/mobile-legends-akun-smurf-sultan-bp-64k-gratis-pilih-1-hero-ryujin-gage/1038381"
WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK')

def cek_stok():
    # Menggunakan cloudscraper untuk melewati proteksi Cloudflare
    scraper = cloudscraper.create_scraper()
    
    try:
        response = scraper.get(URL_PRODUK)
        if response.status_code != 200:
            print(f"Gagal akses web (Status: {response.status_code})")
            return

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Mencari teks "Stok" dengan cara baru (menghindari DeprecationWarning)
        # Kita cari elemen yang mengandung kata 'Stok'
        stok_element = soup.find(string=lambda t: "Stok" in t if t else False)
        
        if stok_element:
            stok_teks = stok_element.strip()
            pesan = f"📢 **Update Stok Itemku!**\n**Produk:** Akun Smurf Sultan\n**Status:** {stok_teks}\n**Link:** {URL_PRODUK}"
            
            # Kirim ke Discord
            scraper.post(WEBHOOK_URL, json={"content": pesan})
            print(f"Berhasil! Data ditemukan: {stok_teks}")
        else:
            print("Teks 'Stok' masih tidak ditemukan di halaman. Cek link atau struktur web.")
            
    except Exception as e:
        print(f"Terjadi error: {e}")

if __name__ == "__main__":
    cek_stok()
