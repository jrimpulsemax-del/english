# English AI SaaS (FastAPI Starter)

Projeto inicial de backend para um SaaS robusto de ensino de inglês com IA.

## 1) Plano de arquitetura completo

### Visão macro (modular monolith evolutivo)
- **Frontend Web**: Next.js (portal do aluno + painel admin), Tailwind, WebSocket para feedback em tempo real.
- **Backend API**: FastAPI (REST + WebSocket), autenticação JWT, orquestração de IA, billing e integrações.
- **Workers assíncronos**: Celery + Redis para tarefas longas (processar áudio, enviar mensagens WhatsApp/Telegram, geração de relatórios).
- **Banco transacional**: PostgreSQL (usuários, assinaturas, progresso, sessões, planos de estudo).
- **Cache/filas**: Redis (rate limit, sessão temporária, fila de jobs).
- **Armazenamento de mídia**: S3-compatible (áudios de prática, feedbacks gravados, assets).
- **Observabilidade**: OpenTelemetry + Prometheus + Grafana + Sentry.
- **Auth e segurança**: JWT + refresh token, RBAC (student/admin/tutor), criptografia em trânsito (TLS), auditoria.

### Componentes backend recomendados
1. **Identity Service**: cadastro, login, reset de senha, roles/permissões.
2. **Learning Service**: estudo personalizado, trilhas, exercícios, avaliação contínua.
3. **Conversation AI Service**: chat e voz, transcrição, feedback gramatical/pronúncia.
4. **Billing Service**: Stripe/Pagar.me para assinatura recorrente, webhook de eventos.
5. **Messaging Integrations Service**: WhatsApp (Meta Cloud API/Twilio), Telegram Bot API.
6. **Admin Service**: métricas de retenção, engajamento, MRR, churn, gerenciamento de conteúdo.

### Escalabilidade
- Deploy em Kubernetes (ou ECS) com autoscaling horizontal.
- API stateless + Redis para estado temporário.
- Postgres com read replicas e particionamento para tabelas de eventos/conversas.
- CDN para assets estáticos.
- Rate limiting por IP/tenant e circuit breaker em provedores externos.

---

## 2) Projeto inicial de backend (FastAPI)

### Funcionalidades implementadas
- CRUD essencial de usuários (`create`, `list`, `read_me`, `update_me`, `delete_me`).
- Autenticação JWT (`/auth/login`).
- Integração de IA com OpenAI (chat + transcrição de áudio), com fallback mock quando `OPENAI_API_KEY` não está definido.

### Estrutura de pastas
```bash
app/
  core/        # config e segurança
  db/          # engine, sessão e base SQLAlchemy
  models/      # entidades User, StudyPlan, ConversationMessage
  routers/     # endpoints auth, users, ai
  schemas/     # contratos de request/response
  services/    # integração OpenAI
  main.py      # bootstrap da API
scripts/
  run_local.sh
```

---

## 3) Endpoints de conversação e plano personalizado

### Auth
- `POST /api/v1/auth/login`

### Usuários
- `POST /api/v1/users`
- `GET /api/v1/users`
- `GET /api/v1/users/me`
- `PUT /api/v1/users/me`
- `DELETE /api/v1/users/me`

### IA (texto e áudio)
- `POST /api/v1/ai/conversation/text`
- `POST /api/v1/ai/conversation/audio` (multipart/form-data com arquivo `audio/*`)
- `POST /api/v1/ai/study-plan`

---

## 4) Exemplos de payloads/respostas

### Criar usuário
```http
POST /api/v1/users
Content-Type: application/json

{
  "email": "ana@example.com",
  "full_name": "Ana Costa",
  "password": "StrongPass123!",
  "english_level": "A2"
}
```

### Login
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "ana@example.com",
  "password": "StrongPass123!"
}
```

Resposta:
```json
{
  "access_token": "<jwt>",
  "token_type": "bearer"
}
```

### Conversação por texto
```http
POST /api/v1/ai/conversation/text
Authorization: Bearer <jwt>
Content-Type: application/json

{
  "message": "I have difficult to speak in meetings.",
  "context": "Business English"
}
```

Resposta:
```json
{
  "reply": "You can say: 'I have difficulty speaking in meetings.' Let's practice a short sentence now.",
  "feedback": "Use 'difficulty' (noun) instead of 'difficult' in this sentence."
}
```

### Conversação por áudio
```bash
curl -X POST 'http://localhost:8000/api/v1/ai/conversation/audio' \
  -H 'Authorization: Bearer <jwt>' \
  -F 'audio=@sample.webm;type=audio/webm'
```

### Geração de plano de estudo
```http
POST /api/v1/ai/study-plan
Authorization: Bearer <jwt>
Content-Type: application/json

{
  "goal": "Falar com fluência em entrevistas internacionais",
  "weekly_hours": 6,
  "deadline_weeks": 12
}
```

Resposta:
```json
{
  "id": 1,
  "goal": "Falar com fluência em entrevistas internacionais",
  "weekly_hours": 6,
  "plan_markdown": "# Plano de estudo...",
  "created_at": "2026-02-26T00:00:00Z"
}
```

---

## 5) Estrutura sugerida de banco (PostgreSQL)

### Tabelas-base
1. **users**
   - `id`, `email`, `full_name`, `hashed_password`, `english_level`, `is_active`, `created_at`
2. **conversation_messages**
   - `id`, `user_id`, `role`, `content`, `source(text/audio)`, `created_at`
3. **study_plans**
   - `id`, `user_id`, `goal`, `weekly_hours`, `plan_markdown`, `created_at`

### Expansão para produção
- `subscriptions`, `invoices`, `payments`, `webhook_events`
- `learning_goals`, `lessons`, `exercise_attempts`, `placement_tests`
- `notifications`, `message_deliveries` (WhatsApp/Telegram)
- `admin_audit_logs`, `feature_flags`, `tenant_settings`

---

## 6) Dependências e script para rodar localmente

### Dependências principais
- `fastapi`, `uvicorn`
- `sqlalchemy`, `psycopg2-binary`
- `python-jose`, `passlib[bcrypt]`
- `openai`
- `python-multipart`
- `pydantic-settings`
- `alembic`

### Instalação e execução
```bash
cp .env.example .env
./scripts/run_local.sh
```

A API estará em `http://localhost:8000` e docs em `http://localhost:8000/docs`.

---

## Variáveis de ambiente
Consulte `.env.example`:
- `DATABASE_URL`
- `JWT_SECRET_KEY`
- `ACCESS_TOKEN_EXPIRE_MINUTES`
- `OPENAI_API_KEY`
- `OPENAI_CHAT_MODEL`
- `OPENAI_AUDIO_TRANSCRIPTION_MODEL`

## Próximos passos recomendados
1. Adicionar migrations com Alembic.
2. Implementar refresh token + logout seguro.
3. Adicionar Stripe para billing.
4. Criar worker para envio e lembretes WhatsApp/Telegram.
5. Adicionar testes automatizados (pytest) e CI/CD.
