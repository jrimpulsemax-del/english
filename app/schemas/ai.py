from datetime import datetime

from pydantic import BaseModel


class ConversationTextRequest(BaseModel):
    message: str
    context: str | None = None


class ConversationResponse(BaseModel):
    reply: str
    feedback: str


class StudyPlanRequest(BaseModel):
    goal: str
    weekly_hours: int
    deadline_weeks: int


class StudyPlanResponse(BaseModel):
    id: int
    goal: str
    weekly_hours: int
    plan_markdown: str
    created_at: datetime

    class Config:
        from_attributes = True
