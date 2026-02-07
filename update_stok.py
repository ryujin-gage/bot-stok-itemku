import os
import asyncio
from playwright.async_api import async_playwright
import requests
import re

# Konfigurasi
URL_PRODUK = "https://www.itemku.com/dagangan/fish-it-1x1x1x1-comet-shark-ryujin-gage/4043761"
WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK')

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
            await page.wait_for_timeout(20000) # Tunggu render maksimal

            # 1. Ambil Nama Produk
            nama_produk = await page.title()
            nama_produk = nama_produk.split('|')[0].strip()

            # 2. Ambil Seluruh Teks Halaman untuk Filter
            halaman_teks = await page.evaluate("() => document.body.innerText")
            
            # 3. Logika Cek Stok (Tersedia/Habis)
            # Kita cari kata 'Stok' atau cek apakah ada tombol 'Beli Sekarang'
            match_stok = re.search(r"Stok:\s*([\w\d]+)", halaman_teks, re.IGNORECASE)
            
            status_stok = "Stok Habis ❌"
            warna_embed = 15158332 # Merah
            
            if match_stok:
                sisa = match_stok.group(1)
                status_stok = f"Tersedia ({sisa}) ✅"
                warna_embed = 3066993 # Hijau
            elif "Terakhir" in halaman_teks:
                status_stok = "Tersedia (Terakhir/1) ⚠️"
                warna_embed = 15105570 # Oranye

            # 4. Cek Status Penjual (Terakhir Online)
            match_online = re.search(r"Terakhir online\s*(.*)", halaman_teks, re.IGNORECASE)
            status_penjual = match_online.group(0).split('\n')[0] if match_online else "Tidak diketahui"

            # 5. Cek Label Pengiriman Instan
            is_instan = "Pengiriman Instan" in halaman_teks
            label_instan = "⚡ Pengiriman Instan Terdeteksi" if is_instan else "🐢 Pengiriman Standar"

            print(f"Update: {nama_produk} - {status_stok}")

            # --- KIRIM KE DISCORD ---
            if WEBHOOK_URL:
                payload = {
                    "embeds": [{
                        "title": f"🔔 UPDATE PRODUK: {nama_produk}",
                        "description": (
                            f"**Status Stok:** `{status_stok}`\n"
                            f"**Info Pengiriman:** `{label_instan}`\n"
                            f"**Status Penjual:** `{status_penjual}`\n\n"
                            f"[Klik untuk Cek/Beli Produk]({URL_PRODUK})"
                        ),
                        "color": warna_embed,
                        "footer": {"text": "Bot Monitor Itemku • Pengiriman Instan Aktif"}
                    }]
                }
                requests.post(WEBHOOK_URL, json=payload)

        except Exception as e:
            print(f"Error: {e}")
            if WEBHOOK_URL and "Timeout" in str(e):
                requests.post(WEBHOOK_URL, json={"content": "⚠️ Bot Timeout saat mengecek Itemku."})
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(cek_stok())
