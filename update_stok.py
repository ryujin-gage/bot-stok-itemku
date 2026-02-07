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
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        try:
            print("Membuka halaman...")
            await page.goto(URL_PRODUK, wait_until="networkidle", timeout=60000)
            
            # Tunggu render tombol stok
            await page.wait_for_timeout(8000)

            # --- CARA BARU: Cari teks yang mengandung kata 'Stok' ---
            # Kita cari elemen yang contains text 'Stok'
            stok_locator = page.locator("text=/Stok:/i")
            
            if await stok_locator.count() > 0:
                # Ambil teks dari elemen stok pertama yang ketemu
                full_text = await stok_locator.first.inner_text()
                print(f"BERHASIL! Data ditemukan: {full_text}")

                if WEBHOOK_URL:
                    status_warna = 15105570 if "Terakhir" in full_text else 3066993
                    payload = {
                        "embeds": [{
                            "title": "⚠️ Update Stok Itemku",
                            "description": f"**Kondisi:** {full_text}\nSegera sikat sebelum habis!",
                            "url": URL_PRODUK,
                            "color": status_warna
                        }]
                    }
                    requests.post(WEBHOOK_URL, json=payload)
            else:
                print("Teks 'Stok:' tidak terdeteksi di DOM. Coba ambil teks body...")
                body_content = await page.inner_text("body")
                if "Terakhir" in body_content:
                    print("Kata 'Terakhir' ditemukan di body!")
                    requests.post(WEBHOOK_URL, json={"content": f"🔥 **STOK LIMIT!** Status: Terakhir. Cek: {URL_PRODUK}"})
                else:
                    print("Gagal menemukan informasi stok.")

        except Exception as e:
            print(f"Error: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(cek_stok())
