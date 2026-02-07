import os
import asyncio
from playwright.async_api import async_playwright
import requests

# Konfigurasi
URL_PRODUK = "https://www.itemku.com/dagangan/fish-it-1x1x1x1-comet-shark-ryujin-gage/4043761"
WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK')

async def cek_stok():
    async with async_playwright() as p:
        # Menjalankan browser chromium
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        try:
            print("Membuka halaman Itemku...")
            # Menggunakan 'commit' untuk menghindari timeout karena iklan/tracker
            await page.goto(URL_PRODUK, wait_until="commit", timeout=90000)
            
            # Tunggu render komponen utama
            await page.wait_for_timeout(15000)

            # --- STRATEGI 1: Ambil angka dari atribut 'max' di kotak input ---
            # Berdasarkan gambar, angka stok berada di elemen input
            input_stok = page.locator("input[type='number']").first
            
            sisa_stok = "Tidak terdeteksi"
            
            if await input_stok.is_visible():
                # Atribut 'max' biasanya berisi total stok yang tersedia
                max_val = await input_stok.get_attribute("max")
                if max_val and max_val != "0":
                    sisa_stok = max_val
                else:
                    # Jika max tidak ada, ambil nilai yang tertulis saat ini
                    sisa_stok = await input_stok.get_attribute("value")

            # --- STRATEGI 2: Cadangan jika teks 'Terakhir' muncul ---
            if sisa_stok == "Tidak terdeteksi" or sisa_stok == "0":
                body_text = await page.evaluate("() => document.body.innerText")
                if "Terakhir" in body_text:
                    sisa_stok = "Terakhir (1)"

            print(f"Hasil Analisis Stok: {sisa_stok}")

            # --- KIRIM KE DISCORD ---
            if WEBHOOK_URL:
                # Tentukan warna dan urgency
                is_limit = "terakhir" in sisa_stok.lower() or sisa_stok == "1"
                
                payload = {
                    "content": "@everyone 🔥 STOK MENIPIS!" if is_limit else "📦 Update Stok Berkala",
                    "embeds": [{
                        "title": "🛒 Informasi Stok Itemku",
                        "description": f"**Sisa Stok saat ini:** `{sisa_stok}`\n\n[Klik untuk Beli Sekarang]({URL_PRODUK})",
                        "color": 15105570 if is_limit else 3066993,
                        "footer": {"text": "Gaskeun sebelum kehabisan!"},
                        "timestamp": None
                    }]
                }
                requests.post(WEBHOOK_URL, json=payload)
                print("Notifikasi berhasil dikirim ke Discord.")

        except Exception as e:
            print(f"Terjadi kesalahan: {e}")
            if WEBHOOK_URL and "Timeout" in str(e):
                requests.post(WEBHOOK_URL, json={"content": "⚠️ Bot Timeout saat akses Itemku. Mencoba lagi sesi berikutnya."})
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(cek_stok())
