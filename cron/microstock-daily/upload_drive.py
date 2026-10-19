#!/usr/bin/env python3
"""
Upload one day's microstock output to Google Drive + append to a summary Sheet.

Run with gvenv python (has googleapiclient). Usage:
  upload_drive.py <output_dir>      # e.g. /root/microstock/output/2026-10-19

Behaviour:
  - root folder "Microstock" (created once, reused)
  - child folder "<date>"
  - upload every png/<id>.png and svg/<id>.svg (as-is, binary)
  - upload manifest.csv as a Google Sheet (drive-native, so it's viewable)
  - append one row per asset to summary Sheet "Microstock Ringkasan" (tab "Aset")

Prints one line per asset: id<TAB>png_link<TAB>svg_link
Exits 0 on full success, non-zero on failure (caller only deletes local on 0).
"""
import sys, os, json, io, datetime

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseUpload

TOKEN = "/root/.hermes/google_token.json"
ROOT_NAME = "Microstock"
SUMMARY_NAME = "Microstock Ringkasan"
SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/spreadsheets",
]


def creds():
    d = json.load(open(TOKEN))
    c = Credentials(
        token=d.get("access_token"),
        refresh_token=d.get("refresh_token"),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=d.get("client_id"),
        client_secret=d.get("client_secret"),
        scopes=d.get("scopes") or SCOPES,
    )
    if not c.valid:
        c.refresh(Request())
    return c


def find_or_create_folder(drive, name, parent=None):
    q = f"name = '{name.replace(chr(39), '')}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    if parent:
        q += f" and '{parent}' in parents"
    r = drive.files().list(q=q, fields="files(id,name)", pageSize=1).execute()
    if r.get("files"):
        return r["files"][0]["id"]
    meta = {"name": name, "mimeType": "application/vnd.google-apps.folder"}
    if parent:
        meta["parents"] = [parent]
    f = drive.files().create(body=meta, fields="id").execute()
    return f["id"]


def find_file(drive, name, parent):
    q = (f"name = '{name.replace(chr(39), '')}' and trashed = false "
         f"and '{parent}' in parents")
    r = drive.files().list(q=q, fields="files(id,name)", pageSize=1).execute()
    return r["files"][0]["id"] if r.get("files") else None


def upload_file(drive, local_path, name, parent, mime=None):
    media = MediaFileUpload(local_path, mimetype=mime, resumable=True)
    body = {"name": name, "parents": [parent]}
    f = drive.files().create(body=body, media_body=media, fields="id,webViewLink").execute()
    return f["id"], f.get("webViewLink", "")


def ensure_aset_tab(sheets, sid):
    ss = sheets.spreadsheets().get(spreadsheetId=sid, fields="sheets(properties)").execute()
    for s in ss["sheets"]:
        if s["properties"]["title"] == "Aset":
            return
    # rename the first tab to "Aset"
    old = ss["sheets"][0]["properties"]["sheetId"]
    sheets.spreadsheets().batchUpdate(
        spreadsheetId=sid,
        body={"requests": [{"updateSheetProperties": {
            "properties": {"sheetId": old, "title": "Aset"},
            "fields": "title"}}]},
    ).execute()


def get_or_create_summary(drive, sheets):
    q = (f"name = '{SUMMARY_NAME}' and mimeType = "
         f"'application/vnd.google-apps.spreadsheet' and trashed = false")
    r = drive.files().list(q=q, fields="files(id,name,parents)", pageSize=1).execute()
    if r.get("files"):
        sid = r["files"][0]["id"]
    else:
        body = {"name": SUMMARY_NAME, "mimeType": "application/vnd.google-apps.spreadsheet"}
        f = drive.files().create(body=body, fields="id").execute()
        sid = f["id"]
    ensure_aset_tab(sheets, sid)
    # write header (idempotent)
    sheets.spreadsheets().values().update(
        spreadsheetId=sid, range="Aset!A1:I1",
        valueInputOption="RAW",
        body={"values": [[
            "tanggal", "id", "kategori", "judul", "deskripsi",
            "keywords", "reject", "png_link", "svg_link"]]},
    ).execute()
    return sid


def main():
    out_dir = sys.argv[1]
    day = os.path.basename(out_dir.rstrip("/"))
    png_dir = os.path.join(out_dir, "png")
    svg_dir = os.path.join(out_dir, "svg")
    manifest = os.path.join(out_dir, "manifest.csv")

    c = creds()
    drive = build("drive", "v3", credentials=c)
    sheets = build("sheets", "v4", credentials=c)

    root_id = find_or_create_folder(drive, ROOT_NAME)
    day_id = find_or_create_folder(drive, day, parent=root_id)

    # read manifest
    rows = {}
    if os.path.exists(manifest):
        import csv
        with open(manifest) as f:
            rd = csv.DictReader(f)
            for r in rd:
                rows[r["id"]] = r

    summary_id = get_or_create_summary(drive, sheets)

    # upload png + svg
    results = []
    sheet_rows = []
    ids = sorted(rows.keys()) or sorted(
        os.path.splitext(f)[0] for f in os.listdir(png_dir) if f.endswith(".png")
    )
    for aid in ids:
        row = rows.get(aid, {})
        png_path = os.path.join(png_dir, aid + ".png")
        svg_path = os.path.join(svg_dir, aid + ".svg")
        png_link = svg_link = ""
        if os.path.exists(png_path):
            _, png_link = upload_file(drive, png_path, aid + ".png", day_id, "image/png")
        if os.path.exists(svg_path):
            _, svg_link = upload_file(drive, svg_path, aid + ".svg", day_id, "image/svg+xml")
        results.append((aid, png_link, svg_link))
        sheet_rows.append([
            day, aid, row.get("category", ""), row.get("title", ""),
            row.get("description", ""), row.get("keywords", ""),
            row.get("reject", ""), png_link, svg_link,
        ])

    # upload manifest.csv as a Google Sheet (viewable in Drive)
    if os.path.exists(manifest) and day_id:
        m_media = MediaFileUpload(manifest, mimetype="text/csv", resumable=True)
        drive.files().create(
            body={"name": "manifest.csv", "parents": [day_id],
                  "mimeType": "application/vnd.google-apps.spreadsheet"},
            media_body=m_media, fields="id").execute()

    # append sheet rows
    if sheet_rows:
        sheets.spreadsheets().values().append(
            spreadsheetId=summary_id, range="Aset!A:I",
            valueInputOption="RAW", insertDataOption="INSERT_ROWS",
            body={"values": sheet_rows}).execute()

    for aid, pl, sl in results:
        print(f"{aid}\t{pl}\t{sl}")
    print(f"OK\t{len(results)} assets -> Drive folder '{day}' + sheet {summary_id}")


if __name__ == "__main__":
    main()