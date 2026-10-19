# Microstock Aset Harian

Pipeline otomasi harian yang menghasilkan aset microstock (gambar PNG + vektor
SVG + metadata) dan mengunggahnya ke Google Drive.

## Cara kerja (`run_daily.sh` → `pipeline.py`)

1. **research** — pilih N subjek aman dari `subjects.json` (kolam dikurasi).
2. **generate** — `qwen-image-3.0-pro` (Kenari) → PNG (base64).
3. **curate** — model vision `qwen3-8-omni-flash:free` menilai tiap aset;
   nilai di bawah ambang (`MIN_SCORE = 7.0`) digenerate ulang sekali.
4. **vectorize** — `vtracer` (PNG → SVG).
5. **metadata** — satu panggilan LLM membuat title/description/keywords/tag
   untuk semua aset.
6. **upload Drive** — `upload_drive.py` naikkan ke folder `Microstock/<tanggal>/`
   + append satu baris per aset ke sheet ringkasan "Microstock Ringkasan".
   Hapus salinan lokal HANYA setelah upload sukses (keluar 0).

## File & peran

| File | Peran |
|---|---|
| `run_daily.sh` | pembungkus yang dipanggil cron (`no_agent`, script-only) |
| `pipeline.py` | tahap 1–5 (research → metadata) |
| `vectorize.py` | PNG → SVG via vtracer |
| `upload_drive.py` | unggah ke Drive + tulis sheet ringkasan |
| `subjects.json` | kolam subjek + style suffix |

## Kredensial & konfigurasi (di luar repo ini)

- API key model: env `HERMES_CUSTOM_API_KENARI_ID_API_KEY`
  (di-set oleh `run_daily.sh` dari `/root/.hermes/.env`).
- Google token: `/root/.hermes/google_token.json` (scope drive + spreadsheets).
- Jumlah aset per run: env `N_ASSETS` (default `10`).

## Catatan ruang lingkup

- Otomasi = riset + generate + metadata (keputusan riil yang dipisah).
- **Upscale & upload ke platform microstock dilakukan manual** — di luar pipeline.