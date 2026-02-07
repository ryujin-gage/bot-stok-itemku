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
            await page.goto(URL_PRODUK, wait_until="domcontentloaded", timeout=120000)
            
            # Auto-scroll untuk memicu render elemen
            await page.evaluate("window.scrollBy(0, 500)")
            await page.wait_for_timeout(5000)
            
            # Tunggu JavaScript stok muat
            await page.wait_for_timeout(25000)

            # Ambil Screenshot untuk dikirim ke Discord
            screenshot_path = "cek_stok.png"
            await page.screenshot(path=screenshot_path)

            # Ambil Data
            nama_produk = await page.title()
            nama_produk = nama_produk.split('|')[0].strip()
            halaman_teks = await page.evaluate("() => document.body.innerText")
            
            # Filter Stok & Online
            match_stok = re.search(r"Stok:\s*([\w\d]+)", halaman_teks, re.IGNORECASE)
            match_online = re.search(r"Terakhir online\s*(.*)", halaman_teks, re.IGNORECASE)
            
            status_stok = "Stok Habis ❌"
            warna_embed = 15158332 # Merah
            
            if match_stok:
                status_stok = f"Tersedia ({match_stok.group(1)}) ✅"
                warna_embed = 3066993 # Hijau
            elif "Terakhir" in halaman_teks:
                status_stok = "Tersedia (Terakhir/1) ⚠️"
                warna_embed = 15105570 # Oranye

            status_penjual = match_online.group(0).split('\n')[0] if match_online else "Status Penjual: Gagal dimuat"
            label_instan = "⚡ Pengiriman Instan" if "Pengiriman Instan" in halaman_teks else "🐢 Pengiriman Standar"

            # --- KIRIM NOTIFIKASI + GAMBAR ---
            if WEBHOOK_URL:
                # Kirim Pesan Embed
                payload = {
                    "embeds": [{
                        "title": f"🔔 MONITOR: {nama_produk}",
                        "description": (
                            f"**Status Stok:** `{status_stok}`\n"
                            f"**Info Pengiriman:** `{label_instan}`\n"
                            f"**Status Penjual:** `{status_penjual}`\n\n"
                            f"[Klik di Sini untuk Beli]({URL_PRODUK})"
                        ),
                        "color": warna_embed,
                        "image": {"url": "attachment://cek_stok.png"},
                        "footer": {"text": "Update Otomatis dengan Screenshot"}
                    }]
                }
                
                # Kirim file gambar menggunakan format multipart/form-data
                with open(screenshot_path, 'rb') as f:
                    requests.post(WEBHOOK_URL, data={"payload_json": asyncio.get_event_loop().run_in_executor(None, lambda: str(payload))}, files={"file": f})
                
                print(f"Berhasil: {status_stok} + Gambar Terkirim")

        except Exception as e:
            print(f"Error: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(cek_stok())
