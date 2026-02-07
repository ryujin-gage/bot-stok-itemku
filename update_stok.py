import os
import asyncio
from playwright.async_api import async_playwright
import requests
import re

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
            # Pindah ke 'domcontentloaded' agar lebih stabil daripada 'commit'
            await page.goto(URL_PRODUK, wait_until="domcontentloaded", timeout=120000)
            
            # TUNGGU KRUSIAL: Tunggu sampai salah satu elemen kunci muncul (misal: tombol beli atau harga)
            # Kita kasih waktu ekstra 30 detik untuk loading script berat
            await page.wait_for_timeout(30000)

            # Ambil Judul & Teks
            nama_produk = await page.title()
            nama_produk = nama_produk.split('|')[0].strip()
            halaman_teks = await page.evaluate("() => document.body.innerText")
            
            # --- PENYARINGAN DATA ---
            # Cari Stok
            match_stok = re.search(r"Stok:\s*([\w\d]+)", halaman_teks, re.IGNORECASE)
            
            # Cari Status Online
            match_online = re.search(r"Terakhir online\s*(.*)", halaman_teks, re.IGNORECASE)
            status_penjual = match_online.group(0).split('\n')[0] if match_online else "Gagal memuat status"

            # Logika Status Stok
            status_stok = "Stok Habis ❌"
            warna_embed = 15158332 
            
            if match_stok:
                sisa = match_stok.group(1)
                status_stok = f"Tersedia ({sisa}) ✅"
                warna_embed = 3066993
            elif "Terakhir" in halaman_teks:
                status_stok = "Tersedia (Terakhir/1) ⚠️"
                warna_embed = 15105570

            # Cek Pengiriman Instan
            is_instan = "Pengiriman Instan" in halaman_teks
            label_instan = "⚡ Pengiriman Instan" if is_instan else "🐢 Pengiriman Standar"

            if WEBHOOK_URL:
                payload = {
                    "embeds": [{
                        "title": f"🔔 MONITOR: {nama_produk}",
                        "description": (
                            f"**Status Stok:** `{status_stok}`\n"
                            f"**Info Pengiriman:** `{label_instan}`\n"
                            f"**Status Penjual:** `{status_penjual}`\n\n"
                            f"[Link Produk]({URL_PRODUK})"
                        ),
                        "color": warna_embed,
                        "footer": {"text": "Pantauan Terakhir"}
                    }]
                }
                requests.post(WEBHOOK_URL, json=payload)
                print(f"Berhasil update: {status_stok}")

        except Exception as e:
            print(f"Error detail: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(cek_stok())
