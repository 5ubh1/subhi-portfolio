# Cron Jobs — VPS Hermes (produksi)

Lima job otomasi yang berjalan di VPS (Hermes cron scheduler), semua dijadwalkan
**berurutan agar tidak memberatkan VPS** (RAM 4 GB). Satu job = satu akun.

## Jadwal (WIB)

| Waktu | Tugas | Tipe | File |
|---|---|---|---|
| 00:00 | Microstock aset harian | script (`no_agent`) | `microstock-daily/` |
| 00:15 | Riset Shopee — Wishlist Cerdas | agent prompt | `shopee-wishlist-cerdas.md` |
| 00:30 | Riset Shopee — VideoProdukku | agent prompt | `shopee-videoprodukku.md` |
| 00:45 | Riset Benable — Glowsyfi | agent prompt | `benable-glowsyfi.md` |
| 01:15 | Riset Benable — Gadget Pedia | agent prompt | `benable-gadget-pedia.md` |

## Catatan penting

- **Kredensial TIDAK pernah disimpan di sini.** API key model dibaca dari env
  (`HERMES_CUSTOM_API_KENARI_ID_API_KEY`), Google OAuth token dari
  `/root/.hermes/google_token.json` — keduanya di luar repo ini.
- Shopee ×2 dan Benable ×2 adalah **tugas yang sama persis**, hanya beda akun
  (sheet target, niche, handle). Prompt tiap akun sengaja dipisah supaya akun
  bisa diedit sendiri-sendiri tanpa saling menabrak.
- Menulis ke Google Sheet selalu **APPEND** (tidak pernah menimpa baris lama).

## Microstock pipeline

Lihat `microstock-daily/README.md` untuk daftar lengkap tahapan (research →
generate → curate → vectorize → metadata → upload Drive).