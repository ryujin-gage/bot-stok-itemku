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
        context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = await context.new_page()

        try:
            print("Membuka halaman...")
            await page.goto(URL_PRODUK, wait_until="networkidle", timeout=60000)
            await page.wait_for_timeout(10000)

            # Ambil teks body
            halaman_teks = await page.evaluate("() => document.body.innerText")
            
            # --- LOGIKA PENCARIAN STOK ---
            # Cari baris yang mengandung kata "Stok" (case insensitive)
            garis_stok = [line for line in halaman_teks.split('\n') if "stok" in line.lower()]
            
            sisa_stok = "Tidak diketahui"
            
            if garis_stok:
                # Ambil baris pertama yang ada kata stok-nya
                teks_mentah = garis_stok[0] 
                
                # Gunakan Regex untuk ambil angka atau kata "Terakhir" setelah kata "Stok"
                # Sesuai gambar: "Stok: Terakhir" atau "Stok: 10"
                match = re.search(r"Stok:\s*([\w\d]+)", teks_mentah, re.IGNORECASE)
                if match:
                    sisa_stok = match.group(1)
            
            # Kirim Notifikasi
            print(f"Hasil Filter - Sisa Stok: {sisa_stok}")
            
            if WEBHOOK_URL:
                # Jika stok "Terakhir", kita anggap sisa 1
                emoji = "🚨" if sisa_stok.lower() == "terakhir" else "📦"
                
                payload = {
                    "content": f"@everyone" if sisa_stok.lower() == "terakhir" else "",
                    "embeds": [{
                        "title": f"{emoji} INFO STOK TERBARU",
                        "description": f"**Sisa Stok:** `{sisa_stok}`\n**Link:** [Klik di Sini]({URL_PRODUK})",
                        "color": 15105570 if sisa_stok.lower() == "terakhir" else 3066993,
                        "footer": {"text": "Pantau terus sebelum ludes!"}
                    }]
                }
                requests.post(WEBHOOK_URL, json=payload)

        except Exception as e:
            print(f"Error: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(cek_stok())
