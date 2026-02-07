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
            await page.goto(URL_PRODUK, wait_until="commit", timeout=90000)
            
            # Tunggu lebih lama agar JavaScript selesai merender angka stok
            await page.wait_for_timeout(20000)

            # --- TEKNIK SAPU JAGAT ---
            sisa_stok = "Tidak terdeteksi"

            # 1. Coba ambil dari atribut 'value' kotak input (yang ada angka 1-nya)
            input_elemen = page.locator("input.ant-input-number-input").first
            if await input_elemen.is_visible():
                val = await input_elemen.get_attribute("value")
                if val: sisa_stok = val

            # 2. Jika gagal, cari teks "Stok:" dan ambil kata setelahnya
            if sisa_stok == "Tidak terdeteksi":
                all_text = await page.evaluate("() => document.body.innerText")
                if "Stok:" in all_text:
                    # Ambil 10 karakter setelah kata "Stok:"
                    index = all_text.find("Stok:")
                    sisa_stok = all_text[index:index+20].replace("Stok:", "").strip().split('\n')[0]

            # 3. Cek kata kunci "Terakhir"
            if "Terakhir" in sisa_stok or "Terakhir" in (await page.content()):
                sisa_stok = "Terakhir (1)"

            print(f"Hasil Akhir: {sisa_stok}")

            if WEBHOOK_URL:
                is_urgent = "Terakhir" in sisa_stok or sisa_stok == "1"
                payload = {
                    "content": "@everyone 🚨 STOK TIPIS!" if is_urgent else "📦 Update Stok",
                    "embeds": [{
                        "title": "🛒 Laporan Stok Itemku",
                        "description": f"**Sisa Stok:** `{sisa_stok}`\n\n[Cek Produk]({URL_PRODUK})",
                        "color": 15105570 if is_urgent else 3066993
                    }]
                }
                requests.post(WEBHOOK_URL, json=payload)

        except Exception as e:
            print(f"Error: {e}")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(cek_stok())
