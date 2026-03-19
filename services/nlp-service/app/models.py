from enum import Enum

from pydantic import BaseModel, Field


class AnalysisCategory(str, Enum):
    database = "database"
    network = "network"
    authentication = "authentication"
    performance = "performance"
    infrastructure = "infrastructure"
    unknown = "unknown"


class AnalysisSeverity(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class AnalysisRequest(BaseModel):
    text: str = Field(min_length=1, max_length=10_000)


class AnalysisResponse(BaseModel):
    category: AnalysisCategory
    severity: AnalysisSeverity
    confidence: float = Field(ge=0.0, le=1.0)
    entities: list[str] = Field(default_factory=list)

