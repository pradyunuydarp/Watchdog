"""Application configuration for the Watchdog NLP service.

This module keeps runtime configuration isolated from business logic so the
analysis layer can be exercised independently in tests and, later, wired into
multiple transports such as FastAPI and gRPC.
"""

from dataclasses import dataclass
import os


@dataclass(frozen=True, slots=True)
class Settings:
    """Immutable application settings loaded from environment variables."""

    app_name: str = os.getenv("APP_NAME", "watchdog-nlp-service")
    app_env: str = os.getenv("APP_ENV", "development")
    api_host: str = os.getenv("API_HOST", "0.0.0.0")
    api_port: int = int(os.getenv("API_PORT", "8000"))
    log_level: str = os.getenv("LOG_LEVEL", "info")
    default_category: str = os.getenv("DEFAULT_CATEGORY", "unknown")
    default_severity: str = os.getenv("DEFAULT_SEVERITY", "low")
    grpc_service_name: str = os.getenv("GRPC_SERVICE_NAME", "watchdog.nlp.v1.Analyzer")
    grpc_bind_host: str = os.getenv("GRPC_BIND_HOST", "0.0.0.0")
    grpc_bind_port: int = int(os.getenv("GRPC_BIND_PORT", "50051"))
    analysis_base_confidence: float = float(os.getenv("ANALYSIS_BASE_CONFIDENCE", "0.35"))
    analysis_category_boost: float = float(os.getenv("ANALYSIS_CATEGORY_BOOST", "0.25"))
    analysis_severity_boost: float = float(os.getenv("ANALYSIS_SEVERITY_BOOST", "0.2"))
    analysis_entity_boost: float = float(os.getenv("ANALYSIS_ENTITY_BOOST", "0.05"))
    analysis_urgent_boost: float = float(os.getenv("ANALYSIS_URGENT_BOOST", "0.05"))
    analysis_max_confidence: float = float(os.getenv("ANALYSIS_MAX_CONFIDENCE", "0.99"))
    analyzer_backend: str = os.getenv("ANALYZER_BACKEND", "heuristic")
    model_artifact_path: str = os.getenv("MODEL_ARTIFACT_PATH", "artifacts/model-bundle.pt")
    model_architecture: str = os.getenv("MODEL_ARCHITECTURE", "gru")
    model_device: str = os.getenv("MODEL_DEVICE", "cpu")
    training_data_path: str = os.getenv("TRAINING_DATA_PATH", "data/training/incidents.jsonl")
    training_random_seed: int = int(os.getenv("TRAINING_RANDOM_SEED", "42"))
    sequence_epochs: int = int(os.getenv("SEQUENCE_EPOCHS", "12"))
    sequence_batch_size: int = int(os.getenv("SEQUENCE_BATCH_SIZE", "8"))
    sequence_max_vocab_size: int = int(os.getenv("SEQUENCE_MAX_VOCAB_SIZE", "5000"))
    sequence_max_sequence_length: int = int(os.getenv("SEQUENCE_MAX_SEQUENCE_LENGTH", "64"))
    planned_model_encoder_name: str = os.getenv("PLANNED_MODEL_ENCODER_NAME", "set-me-later")
    planned_model_tokenizer_name: str = os.getenv("PLANNED_MODEL_TOKENIZER_NAME", "set-me-later")
    attention_num_heads: int = int(os.getenv("ATTENTION_NUM_HEADS", "8"))
    transformer_model_name: str = os.getenv("TRANSFORMER_MODEL_NAME", "set-me-later")

    def as_health_payload(self) -> dict[str, str]:
        """Return a compact status payload for health endpoints."""

        return {
            "service": self.app_name,
            "environment": self.app_env,
            "transport": "http",
            "analyzer_backend": self.analyzer_backend,
            "model_architecture": self.model_architecture,
            "transformer_model_name": self.transformer_model_name,
        }


settings = Settings()
