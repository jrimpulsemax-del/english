from openai import OpenAI

from app.core.config import settings


class AIService:
    def __init__(self) -> None:
        self.client = OpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None

    def generate_conversation_reply(self, message: str, level: str, context: str | None = None) -> tuple[str, str]:
        if not self.client:
            reply = f"[Mock] Let's practice! You said: '{message}'."
            feedback = '[Mock] Good attempt. Focus on sentence order and verb tense consistency.'
            return reply, feedback

        system_prompt = (
            'You are an English tutor. Answer in English, concise, friendly, and actionable. '
            'After answering, provide one short correction tip.'
        )
        user_prompt = (
            f'Level: {level}. Context: {context or "general conversation"}. '
            f'Learner message: {message}. '
            'Return JSON with fields: reply, feedback.'
        )

        response = self.client.chat.completions.create(
            model=settings.openai_chat_model,
            response_format={'type': 'json_object'},
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt},
            ],
            temperature=0.5,
        )
        content = response.choices[0].message.content or '{}'
        import json

        parsed = json.loads(content)
        return parsed.get('reply', ''), parsed.get('feedback', '')

    def transcribe_audio(self, filename: str, audio_bytes: bytes) -> str:
        if not self.client:
            return '[Mock transcription] I want to improve my speaking confidence.'

        from io import BytesIO

        buffer = BytesIO(audio_bytes)
        buffer.name = filename
        transcript = self.client.audio.transcriptions.create(
            model=settings.openai_audio_transcription_model,
            file=buffer,
        )
        return transcript.text

    def generate_study_plan(self, level: str, goal: str, weekly_hours: int, deadline_weeks: int) -> str:
        if not self.client:
            return (
                f"# Plano de estudo ({deadline_weeks} semanas)\n"
                f"- Nível atual: {level}\n"
                f"- Meta: {goal}\n"
                f"- Carga semanal: {weekly_hours}h\n"
                "\n## Semana 1\n- 3 sessões de listening\n- 2 sessões de speaking guiado\n"
            )

        prompt = (
            'Crie um plano de estudo em markdown para inglês com tarefas semanais, métricas e revisão. '
            f'Nível: {level}; meta: {goal}; horas semanais: {weekly_hours}; prazo: {deadline_weeks} semanas.'
        )
        response = self.client.chat.completions.create(
            model=settings.openai_chat_model,
            messages=[{'role': 'user', 'content': prompt}],
            temperature=0.4,
        )
        return response.choices[0].message.content or ''


ai_service = AIService()
