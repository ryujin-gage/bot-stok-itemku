import os
import asyncio
from playwright.async_api import async_playwright
import requests

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
            print("Membuka halaman...")
            await page.goto(URL_PRODUK, wait_until="domcontentloaded", timeout=90000)
            
            # Tunggu 25 detik agar semua JavaScript selesai loading
            await page.wait_for_timeout(25000)

            # --- AMBIL SCREENSHOT UNTUK BUKTI ---
            await page.screenshot(path="bukti_bot.png")

            # --- CARA SCAN SEMUA ELEMEN ---
            halaman_teks = await page.evaluate("() => document.body.innerText")
            
            sisa_stok = "Tidak terdeteksi"
            
            # Cek apakah ada kata "Terakhir" (seperti di gambar kamu)
            if "Terakhir" in halaman_teks:
                sisa_stok = "Terakhir (1)"
            else:
                # Cari pola angka yang biasanya ada di dekat tombol stok
                import re
                match = re.search(r"Stok[:\s]+(\d+)", halaman_teks, re.IGNORECASE)
                if match:
                    sisa_stok = match.group(1)

            print(f"Hasil Akhir: {sisa_stok}")

            if WEBHOOK_URL:
                is_urgent = "Terakhir" in sisa_stok or sisa_stok == "1"
                payload = {
                    "content": "@everyone 🚨 STATUS STOK!" if is_urgent else "📦 Pantau Stok",
                    "embeds": [{
                        "title": "🛒 Laporan Stok Itemku",
                        "description": f"**Status Stok:** `{sisa_stok}`\n\nJika tetap tidak terdeteksi, bot sudah mengambil screenshot untuk dicek manual.",
                        "color": 15105570 if is_urgent else 3066993,
                        "url": URL_PRODUK
                    }]
                }
                requests.post(WEBHOOK_URL, json=payload)

        except Exception as e:
            print(f"Error: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(cek_stok())
