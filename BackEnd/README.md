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
LLM_API_KEY=your-server-side-llm-key
BASE_URL=https://api.deepseek.com
MODEL_NAME=deepseek-v4-flash
```

`SUPABASE_SERVICE_ROLE_KEY` must never be exposed to the frontend. Current API calls use the user's Supabase JWT and RLS first; the service role key is reserved for future trusted server-side administration jobs only.

`LLM_API_KEY` must also remain server-side only. AI routes call the provider through Flask and LangChain; the frontend only calls `/api/ai/*`.

## Database Initialization

Open the Supabase SQL Editor. Do not type the local file path into the editor. Open each SQL file in this repository, copy its full contents, paste the SQL into the Supabase SQL Editor, then click **Run**.

Run these files in order:

1. `sql/001_init_schema.sql`
2. `sql/002_rls_policies.sql`
3. `sql/003_seed_data.sql`

Seed data intentionally avoids real `auth.users` ids. The initial tribes and events are public authenticated data with nullable owners.

To manage seeded tribes with a real user:

1. Register or log in once from the frontend so Supabase Auth creates the user.
2. In Supabase Dashboard, open **Authentication > Users** and copy that user's `User UID`.
3. In SQL Editor, replace `YOUR_AUTH_USER_ID` below with the real UUID and run it:

```sql
insert into public.tribe_members (tribe_id, user_id, role)
select id, 'YOUR_AUTH_USER_ID'::uuid, 'owner'
from public.tribes
where name in (
  '编程爱好者',
  '篮球社',
  '吉他社',
  '学术研究会',
  '摄影社',
  '舞蹈社',
  '电影社',
  '志愿者协会'
)
on conflict (tribe_id, user_id)
do update set role = excluded.role;
```

Optionally also mark that user as the `owner_id` on the seed tribes:

```sql
update public.tribes
set owner_id = 'YOUR_AUTH_USER_ID'::uuid
where name in (
  '编程爱好者',
  '篮球社',
  '吉他社',
  '学术研究会',
  '摄影社',
  '舞蹈社',
  '电影社',
  '志愿者协会'
);
```

After this, the user can create, update, and delete events for those tribes through the Flask API because `tribe_members.role = 'owner'` satisfies the RLS manager checks.

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
- `GET /api/events/my-registrations`
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
- Add business-specific AI features on top of the shared LangChain service layer.
