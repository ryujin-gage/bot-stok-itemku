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
            # Timeout ditingkatkan ke 2 menit untuk koneksi lambat
            await page.goto(URL_PRODUK, wait_until="domcontentloaded", timeout=120000)
            
            # JURUS AUTO-SCROLL: Menggulir halaman untuk memicu render elemen
            print("Melakukan auto-scroll untuk memicu render...")
            await page.evaluate("window.scrollBy(0, 600)")
            await page.wait_for_timeout(5000)
            await page.evaluate("window.scrollBy(0, -200)") # Scroll naik sedikit
            
            # Tunggu total 30 detik agar JavaScript stok selesai muat
            await page.wait_for_timeout(25000)

            # Ambil data dasar
            nama_produk = await page.title()
            nama_produk = nama_produk.split('|')[0].strip()
            halaman_teks = await page.evaluate("() => document.body.innerText")
            
            # --- FILTERING DATA ---
            # Cari Status Stok
            match_stok = re.search(r"Stok:\s*([\w\d]+)", halaman_teks, re.IGNORECASE)
            
            # Cari Status Penjual
            match_online = re.search(r"Terakhir online\s*(.*)", halaman_teks, re.IGNORECASE)
            status_penjual = match_online.group(0).split('\n')[0] if match_online else "Status Penjual: Gagal dimuat"

            # Tentukan Status Stok & Warna Embed
            status_stok = "Stok Habis ❌"
            warna_embed = 15158332 # Merah
            
            if match_stok:
                sisa = match_stok.group(1)
                status_stok = f"Tersedia ({sisa}) ✅"
                warna_embed = 3066993 # Hijau
            elif "Terakhir" in halaman_teks:
                status_stok = "Tersedia (Terakhir/1) ⚠️"
                warna_embed = 15105570 # Oranye

            # Cek Label Pengiriman Instan
            label_instan = "⚡ Pengiriman Instan" if "Pengiriman Instan" in halaman_teks else "🐢 Pengiriman Standar"

            # --- KIRIM NOTIFIKASI ---
            if WEBHOOK_URL:
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
                        "footer": {"text": "Update Otomatis via GitHub Actions"}
                    }]
                }
                requests.post(WEBHOOK_URL, json=payload)
                print(f"Update Berhasil Terkirim: {status_stok}")

        except Exception as e:
            print(f"Error detail: {e}")
            if WEBHOOK_URL:
                requests.post(WEBHOOK_URL, json={"content": f"⚠️ Bot Error: `{str(e)[:100]}`"})
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(cek_stok())
