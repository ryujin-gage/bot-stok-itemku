import os
import asyncio
from playwright.async_api import async_playwright
import requests

URL_PRODUK = "https://www.itemku.com/dagangan/fish-it-1x1x1x1-comet-shark-ryujin-gage/4043761"
WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK')

async def cek_stok():
    async with async_playwright() as p:
        # Gunakan mode 'stealth' sederhana dengan menyamar jadi Chrome Windows
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={'width': 1280, 'height': 720},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        try:
            print(f"Membuka halaman...")
            await page.goto(URL_PRODUK, wait_until="domcontentloaded", timeout=60000)
            
            # Tunggu lebih lama agar Cloudflare selesai loading
            await page.wait_for_timeout(10000)

            # Debug: Ambil title halaman untuk cek apakah kita terjebak di Cloudflare
            title = await page.title()
            print(f"Title Halaman: {title}")

            # Mencari elemen yang mengandung info stok (menggunakan selector teks)
            # Kita coba cari elemen yang punya teks angka stok
            stok_element = page.get_by_text("Stok", exact=False).first
            
            if await stok_element.is_visible():
                teks_stok = await stok_element.inner_text()
                print(f"BERHASIL! Ditemukan: {teks_stok}")

                if WEBHOOK_URL:
                    msg = {"content": f"📢 **Update Stok!**\n**Info:** {teks_stok}\n**Link:** {URL_PRODUK}"}
                    requests.post(WEBHOOK_URL, json=msg)
            else:
                print("Gagal menemukan elemen stok. Mencoba ambil screenshot debug...")
                await page.screenshot(path="debug_screenshot.png")
                # Jika title-nya "Just a moment...", berarti terblokir Cloudflare
                if "Just a moment" in title:
                    print("⚠️ Terdeteksi Cloudflare! Script diblokir.")

        except Exception as e:
            print(f"Error: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(cek_stok())
