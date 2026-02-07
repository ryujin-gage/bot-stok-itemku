import os
import asyncio
from playwright.async_api import async_playwright
import requests

URL_PRODUK = "https://www.itemku.com/dagangan/fish-it-1x1x1x1-comet-shark-ryujin-gage/4043761"
WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK')

async def cek_stok():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # Pakai resolusi layar besar biar semua elemen muncul
        context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
        page = await context.new_page()

        try:
            print("Membuka halaman...")
            # Tunggu sampai benar-benar tidak ada aktivitas download lagi
            await page.goto(URL_PRODUK, wait_until="networkidle", timeout=60000)
            
            # Kasih jeda 10 detik buat render JavaScript
            await page.wait_for_timeout(10000)

            # Ambil SELURUH teks yang terlihat di layar
            halaman_teks = await page.evaluate("() => document.body.innerText")
            
            # Cek apakah ada kata "Stok" atau "Terakhir"
            if "Terakhir" in halaman_teks or "Stok" in halaman_teks:
                # Cari baris yang mengandung kata tersebut
                baris_relevan = [b for b in halaman_teks.split('\n') if "Stok" in b or "Terakhir" in b]
                hasil = baris_relevan[0].strip() if baris_relevan else "Stok Terdeteksi"
                
                print(f"HORE! Ketemu: {hasil}")
                
                if WEBHOOK_URL:
                    requests.post(WEBHOOK_URL, json={
                        "content": f"🎯 **STOK UPDATE!**\n**Status:** {hasil}\n**Link:** {URL_PRODUK}"
                    })
            else:
                print("Waduh, masih belum kelihatan juga di teks body.")
                # Kita coba paksa cari elemen angka 1 di kotak stok (sesuai gambarmu)
                await page.screenshot(path="debug.png") # Simpan foto buat bukti

        except Exception as e:
            print(f"Error: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(cek_stok())
