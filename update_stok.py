import os
import asyncio
from playwright.async_api import async_playwright
import requests
import re

# Konfigurasi
URL_PRODUK = "https://www.itemku.com/dagangan/mobile-legends-akun-smurf-sultan-bp-64k-gratis-pilih-1-hero-ryujin-gage/1038381"
WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK')
# URL Foto yang kamu berikan tadi
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
            await page.goto(URL_PRODUK, wait_until="commit", timeout=90000)
            await page.wait_for_timeout(20000)

            # 1. Ambil Nama Produk
            nama_produk = await page.title()
            nama_produk = nama_produk.split('|')[0].strip()

            # --- MANIPULASI STATUS (SELALU AKTIF) ---
            status_stok = "Tersedia ✅" 
            warna_embed = 3066993 # Hijau
            status_penjual = "Online 🟢"

            # Tetap cek label instan (Dibuat selalu kilat sesuai permintaan)
            label_instan = "⚡ Pengiriman Instan"

            print(f"Update Terkirim: {nama_produk} - {status_stok}")

            # --- KIRIM KE DISCORD ---
            if WEBHOOK_URL:
                payload = {
                    "content": "@everyone 🚨 **STOK TERSEDIA!**", # Menambahkan Tag Everyone
                    "embeds": [{
                        "title": f"🔔 UPDATE PRODUK: AKUN SMURF MOBILE LEGENDS BP 77.000+",
                        "description": (
                            f"**Status Stok:** `{status_stok}`\n"
                            f"**Info Pengiriman:** `{label_instan}`\n"
                            f"**Status Penjual:** `{status_penjual}`\n\n"
                            f"[Klik untuk Beli Sekarang]({URL_PRODUK})"
                        ),
                        "color": warna_embed,
                        "image": {"url": URL_FOTO_PRODUK}, # Menambahkan Foto ke Embed
                        "footer": {"text": "Bot Monitor Itemku • Status: Active Always"}
                    }]
                }
                requests.post(WEBHOOK_URL, json=payload)

        except Exception as e:
            print(f"Error: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(cek_stok())
