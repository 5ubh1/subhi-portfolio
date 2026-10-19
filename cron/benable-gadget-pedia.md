# Riset Benable — Gadget Pedia (00.00)

- **Schedule**: `15 1 * * *`
- **Delivery**: `local`
- **Model**: `-`

## Prompt

Tugas: riset produk harian untuk akun Benable `Gadget Pedia` (handle gadgetpedia), lalu tulis hasilnya ke Google Sheet (DUA tab). Bahasa Indonesia, ringkas. Kamu adalah ahli Benable untuk akun ini.

=== SASARAN (HANYA INI) ===
Spreadsheet: Riset Benable — Gadget Pedia
ID: <SHEET_ID:GADGET_PEDIA>
Tab 1: Produk (data per produk)
Tab 2: Konten List (aset siap-tempel per list)

DILARANG: menyentuh spreadsheet lain (termasuk 'Riset Benable — Glowsyfi' ID <SHEET_ID:GLOWSYFI>, 'Riset Pasar Shopee Affiliate — Wishlist Cerdas' ID <SHEET_ID:WISHLIST_CERDAS> dan 'Riset Pasar Shopee Affiliate — VideoProdukku' ID <SHEET_ID:VIDEOPRODUKKU>), mengubah/membuat/menghapus cron lain, mengubah file produksi, atau mengirim DM ke bot/nomor mana pun.

=== AKSES SHEET ===
Python: /root/.hermes/gvenv/bin/python
Kredensial: /root/.hermes/google_token.json (Google OAuth, scope sheets)
Contoh:
  from google.oauth2.credentials import Credentials
  from googleapiclient.discovery import build
  creds = Credentials.from_authorized_user_file('/root/.hermes/google_token.json')
  sh = build('sheets','v4',credentials=creds).spreadsheets()
  sh.values().get(spreadsheetId=SID, range='Produk!A1:I').execute()
Baca dulu seluruh isi DUA tab sebelum menulis. JANGAN menimpa baris yang sudah ada — hanya APPEND baris baru di bawah baris terakhir tiap tab. Tulis script ke /root/.hermes/cache/scratch/ (bukan /tmp).

=== STRUKTUR TAB 1: Produk (9 kolom, JANGAN digeser) ===
A Tanggal | B Title List | C Section | D Kategori | E Produk | F Retailer Terbaik | G Kenapa | H Note Kurator | I Link
Kolom C (Section) WAJIB diisi untuk TIAP produk, nilainya NAMA SECTION tempat produk itu berada (konsisten dengan judul section di Tab 2).

=== STRUKTUR TAB 2: Konten List (7 kolom, JANGAN digeser) ===
A Title List | B Deskripsi List | C Prompt Cover Title List | D Welcome Note | E Prompt Cover Welcome Note | F Title Section | G Deskripsi Section
ATURAN PENTING tab Konten List: 1 BARIS = 1 TITLE SECTION (bukan 1 list). Setiap list = 3 baris berurutan (3 section).
  - Baris PERTAMA tiap list: isi A (Title List), B (Deskripsi List), C (Prompt Cover Title List), D (Welcome Note), E (Prompt Cover Welcome Note), F (judul section 1), G (deskripsi section 1).
  - Baris KEDUA & KETIGA tiap list: kolom A, B, C, D, E DIKOSONGKAN (string kosong), hanya isi F (judul section) & G (deskripsi section).
  - Jadi per list ada 3 baris; total baris baru per run di Tab 2 = 2 list x 3 = 6 baris.
  - JANGAN pakai \n sebagai pemisah section dalam satu sel — satu section = satu cell sendiri di kolom F & G.

=== KONSISTENSI SECTION (WAJIB) ===
Nama section di Tab 1 kolom C harus SAMA PERSIS dengan judul section di Tab 2 kolom F untuk list terkait. Tentukan 3 nama section PER LIST dulu, lalu pakai nama yang sama di kedua tab.

=== NICHE & AUDIENS (kunci) ===
Akun Gadget Pedia = BUDGET TECH / GADGET untuk audiens UMUM (semua gender). 2 kategori: (1) Desk Setup / home office tech, (2) Travel Gadgets. Gaya = KURATOR (hand-picked/curated), BUKAN first-person. JANGAN tulis 'aku pakai / aku tes / aku masih bayar' (akun ini dikurasi, bukan diary pribadi). Framing kurator: 'Best for [kebutuhan]. Why it's picked: [alasan nyata — fitur/harga/trend]. Watch out: [kekurangan / untuk siapa skip].'

=== TARGET PER RUN ===
Hasilkan 40 PRODUK BARU per hari, terbagi rata 2 LIST (~20 item):
  - List A: Desk Setup (keyboard, mouse, monitor stand, lampu meja, docking/hub, webcam, cable management, dll.)
  - List B: Travel Gadgets (power bank, charger/adapter universal, earbuds noise-canceling, organizer kabel, luggage tracker, dll.)
UNTUK TIAP LIST, HASILKAN 3 SECTION yang masuk akal dan sebar ~20 produknya ke 3 section itu secara berimbang (jangan menumpuk di satu section).

=== RETAILER WHITELIST (WAJIB — hanya partner terkonfirmasi) ===
Kolom F (Retailer Terbaik) dan I (Link) HANYA boleh dari retailer partner Benable yang TERKONFIRMASI. Untuk niche gadget/tech, whitelist terkonfirmasi:
  Best Buy (bestbuy.com), eBay (ebay.com).
Amazon adalah partner tapi low-value (rate ~4%, atribusi 24 jam) — JANGAN jadikan default; hanya pakai Amazon bila TIDAK ada di Best Buy/eBay.
JANGAN pakai brand DTC atau retailer yang BELUM terverifikasi sebagai partner Benable: newyork.com/toko brand langsung, newworld, bbg, walmart.com, target.com, homedepot.com — KECUALI produk itu benar-benar TIDAK tersedia di whitelist; kalau terpaksa, tandai di kolom G (Kenapa) dengan teks 'partner belum terverifikasi'.

=== FORMAT LINK (WAJIB: URL halaman produk, BUKAN URL pencarian) ===
Kolom I (Link) harus URL HALAMAN PRODUK spesifik (mengandung /site/<sku>.p?skuId=... di Best Buy, /itm/<id> di eBay, /dp/<ASIN> di Amazon), BUKAN URL pencarian (/search?..., /s?k=..., /sch/i.html?_nkw=...). URL pencarian merusak kartu Benable (foto kosong + judul samar) dan sering tidak di-match jadi tracking link.
Cara mendapat URL produk: cari produk di situs retailer whitelist lewat web_search `site:<retailer.com> <nama produk>`, lalu ambil URL halaman produk dari hasil pencarian (hasil search sudah menampilkan URL produk langsung). JANGAN menulis URL produk yang tidak ditemukan. Kalau URL halaman produk tidak bisa dipastikan untuk suatu produk, LEWATI produk itu lalu ganti dengan produk lain yang URL-nya bisa ditemukan.

ASET LENGKAP di Tab 2 (3 baris per list, satu baris per section):
  1. Title List (hanya baris 1) — judul tajam, catchy, tematik (bukan tumpukan keyword), pola 'Budget Desk Setup Finds Under $50 That Still Feel Premium'. Hasilkan dari riset kata kunci tren kurator di Benable (sinyal publik: benable.com/discover, kategori tech teratas, judul list kreator best-seller).
  2. Deskripsi List (hanya baris 1) — deskripsi list 1-2 kalimat, menjelaskan isi & manfaat list (pelengkap judul). Gaya kurator.
  3. Prompt Cover Title List (hanya baris 1) — prompt teks untuk generate GAMBAR COVER list (flat-lay, banner widescreen ~1000x220 px, tanpa orang, tanpa teks di gambar, sisakan ruang kosong untuk judul). Sebutkan ukuran px + warna palet + komposisi elemen.
  4. Welcome Note (hanya baris 1) — teks sambutan list (gantikan default 'Hi there!'), 2-3 kalimat, gaya kurator, tidak mengaku sudah memakai produk.
  5. Prompt Cover Welcome Note (hanya baris 1) — prompt teks untuk generate GAMBAR cover welcome note (square 1:1, flat-lay produk khas list itu, tanpa orang, tanpa teks).
  6. Title Section (tiap baris) — judul section (2-4 kata), 1 judul per baris di kolom F.
  7. Deskripsi Section (tiap baris) — deskripsi 1 kalimat untuk section tsb, 1 per baris di kolom G, urut sama dengan judul sectionnya.

=== CARA KERJA WAJIB (DELEGASI 4 SUB-AGENT) ===
Di mode cron, web_extract TIDAK bisa membuka halaman produk, dan execute_code / python3 -c DIBLOKIR (tanpa user untuk approve). KARENA ITU ikuti alur ini — JANGAN riset/verifikasi link sendiri, dan JANGAN pakai browser/Chrome (boros RAM, bikin OOM).

1. Kamu (agen utama) TENTUKAN dulu 40 produk + 3 section per list (2 list) memakai web_search untuk nama produk NYATA. Langkah ini tetap bisa.
2. DELEGASIKAN riset link ke 4 SUB-AGENT lewat delegate_task (SATU panggilan, 4 task). Bagi 40 produk jadi 4 kelompok ~10:
   - sub-agen 1 & 2: produk List A
   - sub-agen 3 & 4: produk List B
3. SETIAP sub-agen diberi context lengkap (self-contained): daftar produk (nama + section), whitelist retailer, format URL yang benar, dan instruksi:
   - web_search "site:<retailer> <produk>" untuk mendapat URL halaman produk (URL produk langsung muncul di hasil pencarian — ini SUDAH cukup)
   - JANGAN pakai browser/Chrome — cukup web_search, ringan untuk VPS 4GB
   - kembalikan hasil JSON: [{"produk","retailer","url_terverifikasi","alasan_retailer","note_kurator"}]
   - kalau URL halaman produk tidak bisa dipastikan, LEWATI produk itu (jangan mengarang URL) lalu ganti produk lain yang URL-nya bisa ditemukan
4. Setelah SEMUA sub-agen selesai, kamu RANGKUM hasilnya lalu tulis ke Sheet pakai:
   - write_file untuk simpan script .py ke /root/.hermes/cache/scratch/
   - lalu jalankan: python3 <file>.py   (BUKAN execute_code, BUKAN python3 -c)

=== LANGKAH RISET (per produk, kolom Tab 1) ===
1. Baca Produk existing → daftar produk yang sudah ada (jangan duplikat).
2. Riset via web_search ke sumber teknisi/artikel best-seller (Wirecutter, The Verge, Tom's Guide, RTINGS, dll.) untuk nama produk NYATA. JANGAN mengarang nama produk.
3. Tiap produk, tentukan RETAILER TERBAIK dari WHITELIST di atas (jangan default ke Amazon atau brand DTC).
4. Kolom G (Kenapa): alasan singkat kenapa retailer itu dipilih (partner terkonfirmasi / rate lebih tinggi / atribusi sampai 30 hari / Amazon cuma 24 jam & 4%). Tanpa bukti angka, tulis 'belum terverifikasi' — JANGAN mengarang persentase.
5. Kolom H (Note Kurator): 250–400 karakter, 3+ baris detail non-katalog (fitur nyata, cocok untuk siapa & kapan, kombinasi device, kesalahan umum). Bukan sebaris spesifikasi.
6. Kolom I (Link): URL HALAMAN PRODUK spesifik (BUKAN URL pencarian), dari retailer whitelist, yang ditemukan via web_search. JANGAN short-link ambigu.
7. Cek validitas sebelum menulis: brand & nama harus nyata. Klaim 'viral/trending/best-seller' wajib ada sumber; kalau tidak, buang klaim.

=== ATURAN DIAM vs LAPOR (WAJIB) ===
- SUKSES = minimal 1 baris produk tertulis di Tab 1 (Section + Link halaman produk terisi) DAN aset list tertulis di Tab 2 (6 baris = 2 list x 3 section), terverifikasi via baca-balik (jumlah baris bertambah di KEDUA tab, header tidak geser, kolom A-E kosong di baris section 2 & 3). Respons akhir cukup satu baris: 'OK <n> produk (2 list)'. Output disimpan lokal saja.
- GAGAL / nol baris / tidak bisa akses sheet: respons akhir WAJIB diawali 'GAGAL:' lalu penyebab konkret (HTTP code/pesan error, nama tab, baris) dan apa yang dibutuhkan. DILARANG menutup kegagalan dengan klaim sukses atau mengarang data.
- Jangan menulis harga/rating/persentase yang tidak ditemukan di sumber. 'belum terverifikasi' lebih baik daripada tebakan.

=== BATAS ===
- Jangan menambah/menghapus kolom/tab atau mengubah header (Tab 1: 9 kolom; Tab 2: 7 kolom).
- Jangan mengirim pesan ke Telegram/Discord/email mana pun di luar mekanisme cron ini.
- Jangan mengubah cron lain atau file di luar /root/.hermes/cache/scratch/.