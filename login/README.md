# Login demo (Flask backend)

Standalone feature, unrelated to the Titanic analysis pipeline — deps live in
`login/requirements.txt`, not `analysis/requirements.txt`.

## Setup

```
pip install -r login/requirements.txt
```

Credentials are read from `.env` at the repo root (already gitignored):

```
LOGIN_USERNAME=demo@example.com
LOGIN_PASSWORD_HASH=<output of generate_password_hash(...)>
```

Generate a hash for your own demo password instead of using the one in this
repo:

```
python -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('your-demo-password'))"
```

Paste the result into `LOGIN_PASSWORD_HASH` in `.env`. Never put the plaintext
password there — only the hash.

## Run

```
python login/server.py
```

Serves the page and the API from one process at `http://127.0.0.1:5000/`.
`POST /login` accepts `{"username": "...", "password": "..."}` and returns
`{"success": true/false, "message": "..."}` with `200` on success, `401` on
bad credentials, `429` if rate-limited (5 attempts/minute per IP).

## CI

`.github/workflows/ci.yml` runs a `login-backend-test` job on every push
and PR to `main`: it installs `login/requirements.txt`, starts the server
with disposable CI-only credentials, and hits `POST /login` once with a
correct password (expects `200`) and once with a wrong one (expects `401`).
It never touches the real `.env` credentials.

## Deploying to Render

The repo includes a starter `render.yaml` (repo root) for this Flask app,
and `.github/workflows/ci.yml` has a `deploy` job that fires a Render
deploy hook on every push to `main`, after lint/tests pass. None of this
works until you do the one-time manual setup below — nobody else can do
this part for you, it requires your Render account.

1. **Create a Render account** at https://render.com (free tier is fine).
2. **Create a Web Service** pointed at this GitHub repo
   (`aiwithmaha/mytitanicdatasetproject`):
   - Either use "New + > Blueprint" and let Render read `render.yaml` from
     the repo root, or create a plain "New + > Web Service" and set:
     - Build command: `pip install -r login/requirements.txt`
     - Start command: `gunicorn --chdir . -w 2 -b 0.0.0.0:$PORT login.server:app`
     - Runtime: Python 3 (3.11.x)
3. **Set environment variables** on the Render service (Dashboard >
   Environment): `LOGIN_USERNAME` and `LOGIN_PASSWORD_HASH`, same values
   you'd put in `.env` locally (see "Setup" above). Do not commit these.
4. **Copy the deploy hook URL**: on the Render service page, go to
   Settings > Deploy Hook, copy the URL.
5. **Add it as a GitHub Actions secret**: in this repo, go to
   Settings > Secrets and variables > Actions > New repository secret,
   name it `RENDER_DEPLOY_HOOK_URL`, and paste the URL as the value.

Once the secret is set, every push to `main` that passes CI will call the
hook and Render will redeploy. Until the secret exists, the `deploy` job
logs a warning and exits cleanly (it doesn't fail the pipeline).
