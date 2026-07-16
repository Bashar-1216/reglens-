# Arabic Fonts — Noto Naskh Arabic

The PDF report generator requires **Noto Naskh Arabic** font files.

## Automatic (Docker)

If you build with Docker, the fonts are downloaded automatically during the build process.

## Manual Download

If running locally without Docker, download the fonts manually:

1. Go to: https://fonts.google.com/noto/specimen/Noto+Naskh+Arabic
2. Click "Download family"
3. Extract and copy these files to this `fonts/` directory:
   - `NotoNaskhArabic-Regular.ttf`
   - `NotoNaskhArabic-Bold.ttf`

Or use wget:
```bash
wget -O NotoNaskhArabic-Regular.ttf "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoNaskhArabic/NotoNaskhArabic-Regular.ttf"
wget -O NotoNaskhArabic-Bold.ttf "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoNaskhArabic/NotoNaskhArabic-Bold.ttf"
```

## Fallback

If fonts are not found, the PDF generator will fall back to Helvetica (Arabic text may not render correctly).
