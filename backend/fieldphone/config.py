from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "FieldPhone"
    debug: bool = True

    project_root: Path = Path(__file__).resolve().parent.parent.parent
    data_dir: Path = project_root / "data"
    audio_dir: Path = data_dir / "audio"
    sessions_dir: Path = data_dir / "sessions"
    configs_dir: Path = project_root / "configs"

    database_url: str = f"sqlite:///{project_root / 'data' / 'fieldphone.db'}"

    # Audio processing defaults
    silence_threshold_db: float = -40.0
    min_silence_duration_ms: int = 200
    min_token_duration_ms: int = 100

    # Formant extraction defaults
    max_formant_hz: float = 5500.0
    num_formants: int = 5
    formant_window_length_s: float = 0.025

    # Classifier defaults
    classifier_high_confidence: float = 0.75
    classifier_low_confidence: float = 0.50

    model_config = {"env_prefix": "FIELDPHONE_"}


settings = Settings()
