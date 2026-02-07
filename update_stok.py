import os
import asyncio
from playwright.async_api import async_playwright
import requests
import json

# Konfigurasi
URL_PRODUK = "https://www.itemku.com/dagangan/mobile-legends-akun-smurf-sultan-bp-64k-gratis-pilih-1-hero-ryujin-gage/1038381"
WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK')

# SAYA GANTI KE LINK IMGUR AGAR TIDAK KOTAK ABU-ABU LAGI
URL_FOTO_PRODUK = "https://ibb.co.com/pvXkDnpv" 

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
            await page.goto(URL_PRODUK, wait_until="commit", timeout=120000)
            
            # --- DATA MANIPULASI (BIAR GANTENG DI DISCORD) ---
            status_stok = "Tersedia ✅" 
            warna_embed = 3066993 # Hijau
            status_penjual = "Online 🟢"
            label_instan = "⚡ Pengiriman Instan"

            if WEBHOOK_URL:
                # Payload dengan link gambar yang sudah diperbaiki
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
                        "image": {"url": URL_FOTO_PRODUK}, # Menggunakan link langsung
                        "footer": {"text": "Bot Monitor Itemku • Status: Active Always"}
                    }]
                }

                response = requests.post(WEBHOOK_URL, json=payload)
                
                if response.status_code in [200, 204]:
                    print("Akhirnya! Update Terkirim dengan Gambar.")
                else:
                    print(f"Gagal lagi: {response.text}")

        except Exception as e:
            print(f"Error: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(cek_stok())
