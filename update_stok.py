import os
import asyncio
from playwright.async_api import async_playwright
import requests

# Konfigurasi
URL_PRODUK = "https://www.itemku.com/dagangan/fish-it-1x1x1x1-comet-shark-ryujin-gage/4043761"
WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK')

async def cek_stok():
    async with async_playwright() as p:
        # Jalankan browser (headless=True agar tidak muncul jendela)
        browser = await p.chromium.launch(headless=True)
        # Gunakan User Agent manusia agar tidak dicurigai
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        try:
            print(f"Membuka halaman: {URL_PRODUK}")
            await page.goto(URL_PRODUK, wait_until="networkidle", timeout=60000)

            # Tunggu 5 detik tambahan untuk jaga-jaga render JavaScript
            await page.wait_for_timeout(5000)

            # Ambil semua teks dari halaman
            body_text = await page.inner_text("body")

            if "Stok" in body_text:
                # Cari baris yang mengandung kata "Stok"
                lines = [line for line in body_text.split('\n') if "Stok" in line]
                stok_info = lines[0] if lines else "Stok ditemukan (detail tidak terbaca)"
                
                print(f"Ditemukan: {stok_info}")

                # Kirim ke Discord
                if WEBHOOK_URL:
                    payload = {"content": f"📢 **Update Stok Itemku!**\n**Status:** {stok_info}\n**Link:** {URL_PRODUK}"}
                    requests.post(WEBHOOK_URL, json=payload)
            else:
                print("Teks 'Stok' tetap tidak ditemukan. Mungkin halaman berubah.")

        except Exception as e:
            print(f"Terjadi kesalahan: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(cek_stok())
