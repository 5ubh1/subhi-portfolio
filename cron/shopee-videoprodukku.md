# Riset Shopee — VideoProdukku (00.00)

- **Schedule**: `30 0 * * *`
- **Delivery**: `local`
- **Model**: `-`

## Prompt

Tugas: riset produk Shopee harian untuk akun Pinterest `VideoProdukku`, lalu tulis hasilnya ke Google Sheet. Bahasa Indonesia, ringkas.

=== SASARAN (HANYA INI) ===
Spreadsheet: Riset Pasar Shopee Affiliate — VideoProdukku
ID: <SHEET_ID:VIDEOPRODUKKU>
Tab: Riset_Niche, Produk_Target, Sumber_Riset, Tracker_Pin

DILARANG: menyentuh spreadsheet lain (termasuk Wishlist Cerdas ID <SHEET_ID:WISHLIST_CERDAS>), mengubah/membuat/menghapus cron lain, mengubah file produksi, atau mengirim DM ke bot/nomor mana pun.

=== AKSES SHEET ===
Python: /root/.hermes/gvenv/bin/python
Kredensial: /root/.hermes/google_token.json (Google OAuth, scope sheets)
Contoh:
  from google.oauth2.credentials import Credentials
  from googleapiclient.discovery import build
  creds = Credentials.from_authorized_user_file('/root/.hermes/google_token.json')
  sh = build('sheets','v4',credentials=creds).spreadsheets()
  sh.values().get(spreadsheetId=SID, range='Produk_Target!A1:K').execute()
Baca dulu seluruh Produk_Target sebelum menulis. JANGAN menimpa baris yang sudah ada — hanya APPEND baris baru di bawah baris terakhir. Tulis script ke /root/.hermes/cache/scratch/ (bukan /tmp).

=== STRUKTUR Produk_Target (11 kolom, JANGAN digeser) ===
A Tanggal | B Prioritas | C Niche | D Produk | E Bukti Permintaan | F Harga ID (kisaran) | G Board Pinterest | H Pin (Judul <=50 char) | I Deskripsi Pin | J Status Link Shopee | K Link Shopee
G adalah NAMA BOARD (mis. 'Dapur & Kebersihan'), H adalah JUDUL PIN, I adalah DESKRIPSI. Jangan tertukar. Setelah menulis, verifikasi baca-balik: kolom G harus berisi salah satu dari 5 nama board di bawah, dan len(H) <= 50.

=== BOARD & NICHE (kunci, jangan campur) ===
Skincare Rekomendasi · Fashion & Hijab · Organizer & Storage · Alat Rumah Tangga Cerdas · Dapur & Kebersihan

=== LANGKAH RISET ===
1. Baca Produk_Target existing → daftar produk yang sudah ada (jangan duplikat).
2. Cek Sumber_Riset → pakai URL pencarian Shopee + sumber pihak ketiga yang terdaftar di sana.
3. CATATAN PENTING: shopee.co.id memblokir scraping tanpa login (halaman 'Halaman Tidak Tersedia'). JANGAN buang waktu retry browser ke Shopee. Gunakan web_search + web_extract ke sumber sekunder (blog perbandingan, GoodStats/Compas, statistik marketplace, artikel best-seller Shopee Indonesia tahun berjalan) untuk mendapat nama produk konkret, kisaran harga Rupiah, dan bukti permintaan.
4. Prioritas niche: Home & Living (Alat Rumah Tangga Cerdas + Dapur & Kebersihan) = fokus utama, lalu Skincare, lalu Organizer & Storage, lalu Fashion & Hijab. Prioritaskan board yang paling sedikit pin-nya via Tracker_Pin (kolom B+C) — board dengan 0–2 entri dapat porsi riset lebih besar.
5. Hasilkan 3–6 PRODUK BARU per hari. Tiap produk wajib punya:
   - Prioritas: P1 (bukti permintaan kuat + harga Rp30–150rb) / P2 / P3
   - Bukti Permintaan: angka + sumber, ditulis jujur. Jika tidak ada angka, tulis 'belum terverifikasi' — JANGAN mengarang persentase.
   - Judul Pin <=50 karakter (hitung dengan Python, assert len<=50 sebelum tulis)
   - Deskripsi Pin: 1–2 kalimat manfaat + CTA 'Link Shopee di pin ini, cek sebelum beli!' + hashtag niche
   - Status Link Shopee: 'BELUM ADA'; kolom K (Link Shopee) kosongkan — hanya Subhi yang mengisi link afiliasi.
6. Append temuan tren baru (dengan sumber & kredibilitas) ke Riset_Niche. Kolom (7): Tanggal | Niche | Temuan | Bukti/Angka | Sumber | Kredibilitas | Implikasi untuk Pin. TIDAK ada kolom Board Pinterest di tab ini.
7. Untuk tiap produk baru, append 1 baris ke Tracker_Pin: A (Tanggal) kosong, B = Judul Pin, C = Board, D/E/F (Saves, Klik, CTR) kosong, G (Update) = tanggal hari ini, H (Keterangan) = '<Prioritas> - Draft siap posting - link Shopee belum diisi'.

=== ATURAN DIAM vs LAPOR (WAJIB) ===
- SUKSES = minimal 1 baris produk baru tertulis DAN terverifikasi via baca-balik. Respons akhir cukup satu baris: 'OK <n> produk (<board>)'. Output ini disimpan lokal saja, tidak dikirim ke chat Subhi.
- GAGAL / nol produk tertulis / tidak bisa akses sheet / semua sumber mentah: respons akhir WAJIB diawali persis dengan 'GAGAL:' lalu penyebab konkret (HTTP code atau pesan error, nama tab, baris bermasalah) dan apa yang dibutuhkan untuk memperbaiki. DILARANG menutup kegagalan dengan klaim sukses atau mengarang data.
- Jangan pernah menulis angka harga/persentase yang tidak kamu temukan di sumber. 'belum terverifikasi' lebih baik daripada tebakan.

=== BATAS ===
- Jangan menambah kolom, menghapus tab, atau mengubah header.
- Jangan mengirim pesan ke Telegram/Discord/email mana pun di luar mekanisme cron ini.
- Jangan mengubah cron lain atau file di luar /root/.hermes/cache/scratch/.