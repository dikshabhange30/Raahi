# Raahi frontend (React + Vite)

Put this `frontend` folder next to your `backend` folder:

```
raahi/
  backend/
  frontend/   <- this folder
```

## Run it

1. Start the backend (from `raahi/backend`):
   `uvicorn app.main:app --reload`   (use your real module path)
2. In a second terminal:
   ```
   cd raahi/frontend
   npm install
   npm run dev
   ```
3. Open http://localhost:5173

`.env` already has `VITE_API_BASE_URL=http://localhost:8000`.
Your FastAPI app must allow CORS for `http://localhost:5173` (CORSMiddleware).

## Test each flow
1. Register -> email code -> Verify email -> Login -> email code -> dashboard.
2. Communities: "Start a community", then Join / Leave; filter by city, language, gender.
3. Open a joined community: read and send messages, see members.
4. Member list: "Ask for help" creates a help request.
5. Log in as the other user: Help requests -> Accept -> Open conversation -> chat.
6. Profile: edit fields (gender locks after first save).
7. Safety: block / unblock / report. Admin page appears only if /safety/admin/reports returns 200.

## What works vs what needs backend work
Works: everything above, against your real endpoints.
Needs backend work (optional later):
- No `is_admin` flag in /users/me (admin is detected by calling an admin route).
- No resend-OTP endpoint, so no resend button.
- Chat refreshes every 10 s (polling); no WebSocket, so it is not real-time.
- Help requests / conversations show "user #id" because the API returns ids, not names.
- Community responses have no member count, and gender filter is done in the browser.
- Report status values in the admin dropdown (pending/reviewed/resolved/dismissed) are guesses; edit `STATUSES` in `src/pages/Admin.jsx` to match yours.
