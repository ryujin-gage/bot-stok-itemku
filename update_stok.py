import os
import asyncio
from playwright.async_api import async_playwright
import requests

URL_PRODUK = "https://www.itemku.com/dagangan/fish-it-1x1x1x1-comet-shark-ryujin-gage/4043761"
WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK')

async def cek_stok():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # Sering kali Itemku butuh viewport desktop agar elemen muncul benar
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        try:
            print("Membuka halaman...")
            await page.goto(URL_PRODUK, wait_until="networkidle", timeout=60000)
            
            # Scroll ke bawah sedikit untuk memicu loading elemen stok
            await page.evaluate("window.scrollBy(0, 500)")
            await page.wait_for_timeout(10000) # Tunggu 10 detik agar render selesai

            # --- STRATEGI: Mencari kata "Terakhir" atau "Stok" secara luas ---
            # Kita ambil semua elemen yang mengandung teks "Terakhir" sesuai gambar kamu
            target_text = page.locator("text=/Terakhir|Stok/i")
            
            count = await target_text.count()
            if count > 0:
                # Ambil teks dari elemen yang paling relevan (biasanya yang ada di area harga)
                for i in range(count):
                    txt = await target_text.nth(i).inner_text()
                    if "Terakhir" in txt or ":" in txt:
                        print(f"BERHASIL! Menemukan data: {txt}")
                        
                        if WEBHOOK_URL:
                            payload = {
                                "content": f"🔥 **STOK TERDETEKSI!**\n**Status:** {txt}\n**Link:** {URL_PRODUK}"
                            }
                            requests.post(WEBHOOK_URL, json=payload)
                        return # Keluar jika sudah ketemu

            # Jika metode locator gagal, gunakan pencarian regex pada seluruh teks body
            body_text = await page.inner_text("body")
            if "Terakhir" in body_text:
                print("Kata 'Terakhir' ditemukan di teks body!")
                if WEBHOOK_URL:
                    requests.post(WEBHOOK_URL, json={"content": f"📢 **Update Stok:** Status 'Terakhir' ditemukan! Cek segera: {URL_PRODUK}"})
            else:
                print("Gagal total. Mungkin elemen stok sedang error atau halaman berubah total.")

        except Exception as e:
            print(f"Error: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(cek_stok())
