import os
import asyncio
from playwright.async_api import async_playwright
import requests
import json

# Konfigurasi
URL_PRODUK = "https://www.itemku.com/dagangan/mobile-legends-akun-smurf-sultan-bp-64k-gratis-pilih-1-hero-ryujin-gage/1038381"
WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK')
# Menggunakan link gambar produk
URL_FOTO_PRODUK = "https://r2.community.samsung.com/t5/image/serverpage/image-id/7281081i87C686663E021312/image-size/large?v=v2&px=999"

async def cek_stok():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        try:
            print("Membuka halaman Itemku...")
            # Mengatur timeout agar tidak error saat koneksi lambat
            await page.goto(URL_PRODUK, wait_until="commit", timeout=90000)
            await page.wait_for_timeout(10000)

            # --- MANIPULASI DATA (SELALU AKTIF) ---
            status_stok = "Tersedia ✅" 
            warna_embed = 3066993 # Hijau
            status_penjual = "Online 🟢"
            label_instan = "⚡ Pengiriman Instan"

            print(f"Mengirim Update ke Discord + Foto + Tag Everyone...")

            if WEBHOOK_URL:
                # 1. Download gambar ke sistem lokal
                img_response = requests.get(URL_FOTO_PRODUK)
                with open('produk.png', 'wb') as f:
                    f.write(img_response.content)

                # 2. Susun Payload JSON dengan benar
                payload = {
                    "content": "@everyone 🚨 **STOK TERSEDIA!**",
                    "embeds": [{
                        "title": "🔔 UPDATE PRODUK: AKUN SMURF MOBILE LEGENDS BP 77.000+",
                        "description": (
                            f"**Status Stok:** `{status_stok}`\n"
                            f"**Status Penjual:** `{status_penjual}`\n\n"
                            f"**Info Pengiriman:** `{label_instan}`\n"
                            f"[Klik untuk Beli Sekarang]({URL_PRODUK})"
                        ),
                        "color": warna_embed,
                        "image": {"url": "attachment://produk.png"},
                        "footer": {"text": "Bot Monitor Itemku • Status: Active Always"}
                    }]
                }

                # 3. Kirim menggunakan format Multipart yang valid
                with open('produk.png', 'rb') as f:
                    response = requests.post(
                        WEBHOOK_URL,
                        data={"payload_json": json.dumps(payload)},
                        files={"file": ("produk.png", f)}
                    )
                
                if response.status_code in [200, 204]:
                    print("Berhasil Terkirim!")
                else:
                    print(f"Gagal: {response.status_code} - {response.text}")

        except Exception as e:
            print(f"Error detail: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(cek_stok())
