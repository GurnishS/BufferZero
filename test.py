from yt_dlp import YoutubeDL

url = "https://www.mxplayer.in/show/watch-bindiya-ke-bahubali/season-1/the-davan-empire-online-fdbe24838023f11187378ff48639291c?watch=true"  # replace with your video

ydl_opts = {
    "skip_download": True,
    "quiet": True,
    "no_warnings": True,
}

with YoutubeDL(ydl_opts) as ydl:
    info = ydl.extract_info(url, download=False)
    formats = info.get("formats", [])

# Print table header
print(f"{'ID':<10} {'EXT':<4} {'RESOLUTION':<12} {'FPS':<4} │ {'FILESIZE':<12} {'TBR':<6} {'PROTO':<6} │ {'VCODEC':<12} {'VBR':<6} {'ACODEC':<10} {'ABR':<5} {'ASR':<5} MORE INFO")
print("─" * 140)

# Print rows
for f in formats:
    fmt_id   = f.get("format_id")
    ext      = f.get("ext") or ""
    res      = f.get("resolution") or (f"{f.get('width','?')}x{f.get('height','?')}" if f.get("width") else "audio only")
    fps      = f.get("fps") or ""
    filesize = f.get("filesize") or f.get("filesize_approx")
    filesize = f"~{filesize/1024/1024:.2f}MiB" if filesize else ""
    tbr      = f.get("tbr") or ""
    proto    = f.get("protocol") or ""
    vcodec   = f.get("vcodec") or "audio only"
    vbr      = f.get("vbr") or ""
    acodec   = f.get("acodec") or ""
    abr      = f.get("abr") or ""
    asr      = f.get("asr") or ""

    # Build MORE INFO column
    info_parts = []
    if f.get("format_note"):
        info_parts.append(f["format_note"])
    if f.get("container"):
        info_parts.append(f["container"])
    if f.get("format"):
        if f["format"] not in info_parts:
            info_parts.append(f["format"])
    more_info = ", ".join(info_parts)

    print(f"{fmt_id:<10} {ext:<4} {res:<12} {fps:<4} │ {filesize:<12} {tbr:<6} {proto:<6} │ {vcodec:<12} {vbr:<6} {acodec:<10} {abr:<5} {asr:<5} {more_info}")
