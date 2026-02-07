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
            print("Membuka halaman...")
            # Menggunakan 'commit' agar tidak perlu menunggu seluruh iklan/tracker load (mencegah timeout)
            await page.goto(URL_PRODUK, wait_until="commit", timeout=90000)
            
            # Tunggu manual agar konten utama muncul
            await page.wait_for_timeout(15000)

            # Ambil semua teks dari halaman
            halaman_teks = await page.evaluate("() => document.body.innerText")
            
            # --- LOGIKA PENYARINGAN STOK ---
            # Kita cari kata 'Stok' yang diikuti angka atau kata 'Terakhir'
            # Format di Itemku biasanya: "Stok: 10" atau "Stok: Terakhir"
            match_stok = re.search(r"Stok:\s*([\w\d]+)", halaman_teks, re.IGNORECASE)
            
            sisa_stok = "Tidak terdeteksi"
            if match_stok:
                sisa_stok = match_stok.group(1)
            elif "Terakhir" in halaman_teks:
                # Jika regex gagal tapi ada kata 'Terakhir' dekat elemen stok
                sisa_stok = "Terakhir (1)"

            print(f"Hasil: {sisa_stok}")

            if WEBHOOK_URL:
                is_urgent = sisa_stok.lower() in ["terakhir", "1"]
                payload = {
                    "content": "@everyone 🔥 STOK MENIPIS!" if is_urgent else "📦 Update Stok Berkala",
                    "embeds": [{
                        "title": "🛒 Informasi Stok Itemku",
                        "description": f"**Sisa Stok saat ini:** `{sisa_stok}`\n\n[Klik untuk Beli Sekarang]({URL_PRODUK})",
                        "color": 15105570 if is_urgent else 3066993,
                        "footer": {"text": "Gaskeun sebelum kehabisan!"}
                    }]
                }
                requests.post(WEBHOOK_URL, json=payload)

        except Exception as e:
            print(f"Error: {e}")
            # Jika timeout tetap terjadi, kirim lapor ke Discord agar kamu tahu
            if "Timeout" in str(e) and WEBHOOK_URL:
                requests.post(WEBHOOK_URL, json={"content": "⚠️ Bot sedang sulit mengakses Itemku (Timeout). Akan dicoba lagi otomatis nanti."})
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(cek_stok())
