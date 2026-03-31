# FieldPhone

A phoneme classification and database management tool for field linguists. FieldPhone makes comparative listening — the essential tool for transcriptional judgment — faster, richer, and less tedious.

## Architecture

- **Backend**: Python (FastAPI) — handles audio processing (parselmouth/Praat), acoustic analysis, phonetic queries, and the SQLite database
- **Frontend**: React + TypeScript (Vite) — waveform editing, transcription interface, sortable results tables with inline audio playback
- **Database**: SQLite — single-user, portable, zero-config
- **Audio storage**: Local filesystem with paths stored in the database

## Modules

1. **Data Ingestion & Session Management** — import recordings, segment by silence detection, adjust boundaries, normalize orthographic forms
2. **Phonetic Query Engine** — natural language and regex queries over the transcription database, with context-aware retrieval and comparative listening
3. **Acoustic Vowel Classifier** — formant extraction, Lobanov speaker normalization, IPA candidate ranking with language-relative priors
4. **Transcription Interface** — shorthand expansion, immutable record system, real-time classifier integration, side-by-side comparative listening
5. **Consistency & Quality Audit** — inter-session consistency checking, acoustic-transcription divergence reports, speaker comparison
6. **Tone Analysis Assistant** — F0 extraction, transcription-F0 consistency checking, tonal query retrieval

## Getting Started

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn fieldphone.main:app --reload
```

The API will be available at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The UI will be available at `http://localhost:5173`.

## Configuration

- `configs/phonetic_classes.example.yaml` — define phonetic natural classes for your language's inventory
- `configs/shorthand.example.yaml` — define shorthand-to-IPA expansion mappings

Copy these to `configs/phonetic_classes.yaml` and `configs/shorthand.yaml` and customize for your language.

## Project Structure

```
Field_Phone/
├── backend/
│   ├── fieldphone/
│   │   ├── main.py              # FastAPI application entry point
│   │   ├── config.py            # Application settings
│   │   ├── database.py          # SQLite/SQLAlchemy setup
│   │   ├── models/              # SQLAlchemy ORM models
│   │   ├── schemas/             # Pydantic request/response schemas
│   │   ├── api/                 # API route handlers (one per module)
│   │   └── services/            # Business logic (audio processing, classification, queries)
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── components/          # React components (organized by module)
│       ├── pages/               # Top-level page views
│       ├── hooks/               # Custom React hooks (audio playback, queries)
│       ├── types/               # TypeScript type definitions
│       ├── api/                 # API client
│       └── utils/               # Utilities (phonetic helpers, shorthand expansion)
├── configs/                     # Language-specific configuration files
└── data/                        # Local audio files and SQLite database (gitignored)
```
