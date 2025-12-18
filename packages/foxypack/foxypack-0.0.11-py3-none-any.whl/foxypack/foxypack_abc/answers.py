import uuid
from datetime import date

from pydantic import BaseModel, Field


class AnswersAnalysis(BaseModel):
    """Base Model answers analytics"""

    answer_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    url: str
    social_platform: str
    type_content: str


class AnswersStatistics(BaseModel):
    """Base Model answers analytics"""

    answer_id: uuid.UUID = Field(default_factory=uuid.uuid4)


class AnswersSocialContainer(AnswersStatistics):
    """Base Model social containers"""

    system_id: str
    title: str
    subscribers: int
    creation_date: date | None
    analysis_status: AnswersAnalysis


class AnswersSocialContent(AnswersStatistics):
    """Base Model social сontent"""

    system_id: str
    title: str
    views: int
    publish_date: date | None
    analysis_status: AnswersAnalysis
