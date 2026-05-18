# BackEnd

Flask API for the campus interest tribe and event collaboration platform. The API validates Supabase Auth access tokens, forwards the user JWT to Supabase REST, and relies on PostgreSQL RLS for normal business permissions.

## Setup

```bash
cd BackEnd
conda activate vibecoding
pip install -r requirements.txt
cp .env.example .env
```

Fill `.env` with your Supabase project values:

```bash
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your-anon-public-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-keep-server-side-only
FRONTEND_ORIGIN=http://localhost:5173
```

`SUPABASE_SERVICE_ROLE_KEY` must never be exposed to the frontend. Current API calls use the user's Supabase JWT and RLS first; the service role key is reserved for future trusted server-side administration jobs only.

## Database Initialization

Open the Supabase SQL editor and run these files in order:

1. `sql/001_init_schema.sql`
2. `sql/002_rls_policies.sql`
3. `sql/003_seed_data.sql`

Seed data intentionally avoids real `auth.users` ids. The initial tribes and events are public authenticated data with nullable owners. To manage a seeded tribe, create or update a `tribe_members` row for your real Supabase user id with role `owner` or `admin`, or create a new tribe through the API after login.

## Run

```bash
conda activate vibecoding
python run.py
```

Or:

```bash
conda activate vibecoding
flask --app run.py run --debug --port 5001
```

Health check:

```bash
curl http://localhost:5001/api/health
```

## Frontend Integration

In `FrontEnd/.env`, add:

```bash
VITE_API_BASE_URL=http://localhost:5001/api
```

Then run:

```bash
cd ../FrontEnd
npm run dev
```

Use `FrontEnd/src/services/api.js` to call Flask endpoints. It reads the current Supabase session and automatically sends `Authorization: Bearer <access_token>`.

## API Overview

- `GET /api/health`
- `GET /api/profile/me`
- `PATCH /api/profile/me`
- `GET /api/tribes`
- `GET /api/tribes/my`
- `GET /api/tribes/<tribe_id>`
- `POST /api/tribes`
- `POST /api/tribes/<tribe_id>/join`
- `DELETE /api/tribes/<tribe_id>/leave`
- `GET /api/events`
- `GET /api/events/<event_id>`
- `POST /api/events`
- `PATCH /api/events/<event_id>`
- `DELETE /api/events/<event_id>`
- `POST /api/events/<event_id>/register`
- `DELETE /api/events/<event_id>/register`
- `GET /api/messages`
- `PATCH /api/messages/<message_id>/read`
- `GET /api/dashboard/summary`
- `GET /api/dashboard/events`
- `POST /api/ai/activity-copy`

All responses use:

```json
{
  "success": true,
  "data": {},
  "error": null
}
```

or:

```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable message"
  }
}
```

## Tests

```bash
conda activate vibecoding
pytest
```

## Future TODO

- Add pagination and richer dashboard aggregates.
- Add structured validation for date/time and enum fields.
- Add automated auth and RLS integration tests against a test Supabase project.
- Connect `ai_service.py` to OpenAI, DeepSeek, or another LLM provider.
