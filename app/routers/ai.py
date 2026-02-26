from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.conversation_message import ConversationMessage
from app.models.study_plan import StudyPlan
from app.models.user import User
from app.routers.deps import get_current_user
from app.schemas.ai import ConversationResponse, ConversationTextRequest, StudyPlanRequest, StudyPlanResponse
from app.services.ai_service import ai_service

router = APIRouter(prefix='/ai', tags=['ai'])


@router.post('/conversation/text', response_model=ConversationResponse)
def conversation_text(
    payload: ConversationTextRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    reply, feedback = ai_service.generate_conversation_reply(
        message=payload.message,
        level=current_user.english_level,
        context=payload.context,
    )

    db.add(ConversationMessage(user_id=current_user.id, role='user', content=payload.message, source='text'))
    db.add(ConversationMessage(user_id=current_user.id, role='assistant', content=reply, source='text'))
    db.commit()
    return ConversationResponse(reply=reply, feedback=feedback)


@router.post('/conversation/audio', response_model=ConversationResponse)
async def conversation_audio(
    audio: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not audio.content_type or not audio.content_type.startswith('audio/'):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid audio file')

    audio_bytes = await audio.read()
    transcript = ai_service.transcribe_audio(filename=audio.filename or 'audio.webm', audio_bytes=audio_bytes)
    reply, feedback = ai_service.generate_conversation_reply(
        message=transcript,
        level=current_user.english_level,
        context='spoken practice',
    )

    db.add(ConversationMessage(user_id=current_user.id, role='user', content=transcript, source='audio'))
    db.add(ConversationMessage(user_id=current_user.id, role='assistant', content=reply, source='text'))
    db.commit()
    return ConversationResponse(reply=reply, feedback=feedback)


@router.post('/study-plan', response_model=StudyPlanResponse, status_code=status.HTTP_201_CREATED)
def create_study_plan(
    payload: StudyPlanRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    markdown_plan = ai_service.generate_study_plan(
        level=current_user.english_level,
        goal=payload.goal,
        weekly_hours=payload.weekly_hours,
        deadline_weeks=payload.deadline_weeks,
    )
    plan = StudyPlan(
        user_id=current_user.id,
        goal=payload.goal,
        weekly_hours=payload.weekly_hours,
        plan_markdown=markdown_plan,
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan
