import os
import asyncio
from playwright.async_api import async_playwright
import requests
import json

# Konfigurasi
URL_PRODUK = "https://www.itemku.com/dagangan/mobile-legends-akun-smurf-sultan-bp-64k-gratis-pilih-1-hero-ryujin-gage/1038381"
WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK')
URL_FOTO_PRODUK = "https://i.ibb.co.com/TBhNXr5B/1000683c527-picsay-1.webp" 

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
            
            # --- DATA MANIPULASI ---
            status_stok = "Tersedia ✅" 
            warna_embed = 3066993 # Hijau
            status_penjual = "Online 🟢"
            label_instan = "⚡ Pengiriman Instan"

            if WEBHOOK_URL:
                payload = {
                    "content": "@everyone 🚨 **STOK TERSEDIA!**",
                    "embeds": [{
                        "title": "🔔 UPDATE PRODUK: AKUN SMURF MOBILE LEGENDS BP 77.000+",
                        "description": (
                            f"**Status Stok:** `{status_stok}`\n"
                            f"**Status Penjual:** `{status_penjual}`\n"
                            f"**Info Pengiriman:** `{label_instan}`\n\n"
                            f"**━━━━━━━━━━━━━━━━━━━━━━**\n"
                            f"**↓↓ KLIK TOMBOL DI BAWAH UNTUK BELI ↓↓**\n"
                            f"**[ 🛒 BELI SEKARANG KLIK DI SINI ]({URL_PRODUK})**\n"
                            f"**━━━━━━━━━━━━━━━━━━━━━━**"
                        ),
                        "color": warna_embed,
                        "image": {"url": URL_FOTO_PRODUK}, #
                        "footer": {"text": "Bot Monitor Itemku • Auto-update tiap 12 jam"}
                    }]
                }

                requests.post(WEBHOOK_URL, json=payload)
                print("Update Terkirim!")

        except Exception as e:
            print(f"Error: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(cek_stok())
