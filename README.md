# A little love letter ♡

A complete, single-page Flask birthday keepsake with a session password gate, animated countdown, midnight confetti, three photo spaces, a personal letter, wishes, and playful fortunes. Original design; no purchased template, database, frontend build, or external script required.

## Run locally

Use Python 3.11 or newer.

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
Copy-Item .env.example .env
python -c "import secrets; print(secrets.token_hex(32))"
```

Edit `.env`: set your own `SITE_PASSWORD`, paste the generated random value into `SECRET_KEY`, and personalize both names. Keep `COOKIE_SECURE=false` for local HTTP. Then:

```powershell
.venv\Scripts\python serve.py
```

Open http://localhost:5000. On macOS/Linux use `.venv/bin/python` and `cp .env.example .env`.

## Make it hers

- `.env`: `FIANCE_NAME`, `YOUR_NAME`, `BIRTHDAY_DATE`, `BIRTHDAY_TIMEZONE`.
- Default occasion: **5 December 2026, 00:00 in Asia/Kolkata**. The browser receives an explicit timezone offset and periodically synchronizes with server time. The countdown still runs without a connection once loaded. Reopening a suspended tab checks the date immediately.
- At and after that instant, the page says **Happy birthday**, shows zero on the timer, and plays a short confetti shower. The celebration stays after the date; it does not silently reset to next year. Change `BIRTHDAY_DATE` when you want another occasion.
- `content.json`: edit the letter, photo captions, wishes, and fortunes. Restart the app after content or environment edits.
- Photos: place images in `private_photos/`, then set a photo's `src` to `/photos/your-image.jpg`. These files require login. Keep each image reasonably small, ideally under 1 MB. Empty or broken images display the designed placeholders.
- Public image links: set `src` to an `https://` image URL. The image host must allow embedding. Public URLs are independently public; use local photos for privacy.
- Ordinary `/static/` files are public. Keep personal photos in `private_photos/` rather than `static/`.
- The default letter and captions are editable examples. No names or shared memories have been invented.

## Deploy free on Render (recommended)

1. Upload this project to your own Git repository. Keep `.env` out of Git.
2. In Render, create a **Blueprint** from that repository. `render.yaml` defines the complete free web service. Alternatively create a Python web service with build command `pip install -r requirements.txt` and start command `python serve.py`.
3. Enter `SITE_PASSWORD`; the Blueprint generates `SECRET_KEY`. Set the names and date in the service's environment settings. Keep `COOKIE_SECURE=true` on HTTPS.
4. Deploy and open your `onrender.com` address. Check the password and personalized content before sharing with her.

Local photos are ignored by Git by default. To include selected photos in your private deployment repository, explicitly add only those files (for example, `git add -f private_photos/us.jpg`). Render's runtime disk is ephemeral; bundle photos with the deployment rather than uploading them into a running instance. A Docker build includes local `private_photos` files.

Render's free web services sleep after 15 minutes without requests, so the first visitor may wait for startup. Once the page is open, the countdown and confetti run in the browser. See [Render free service limits](https://render.com/docs/free) and [Flask deployment guide](https://render.com/docs/deploy-flask). No scheduled server job is needed at midnight; the page must be open to display the animation.

**Alternative:** [PythonAnywhere](https://help.pythonanywhere.com/pages/FreeAccountsFeatures) offers one free web app with a renewal/expiry requirement. Install dependencies in a virtual environment, set the environment values, and expose `application = create_app()` from its WSGI configuration (import `create_app` from `app`). Do not run `serve.py` inside WSGI. Check the current account restrictions before choosing it.

## Docker

```sh
docker build -t birthday-letter .
docker run --rm --env-file .env -p 5000:5000 birthday-letter
```

One container serves everything; no database or companion service. The `.env` file is excluded from the image. Set `COOKIE_SECURE=true` when deploying behind HTTPS.

## Privacy and behavior

- The password is checked on the server; it is never included in the page or JavaScript. Signed, HttpOnly, SameSite session cookies last seven days. Logging out clears the session.
- Forms require a CSRF token. Ten incorrect password attempts within five minutes temporarily pause login. This in-memory, global limit suits one small personal site with the supplied single-process server; it resets on restart and is not shared across replicas.
- Use a strong shared password and HTTPS. Changing `SECRET_KEY` invalidates existing sessions. Changing only `SITE_PASSWORD` does not log out already signed-in visitors.
- Reduced-motion preferences disable confetti and movement. The layout supports mobile screens, keyboard navigation, and image failure fallbacks.
- No analytics, tracking, third-party fonts, or CDN scripts. Public photo URLs are the only optional external requests.

## Verify

```powershell
.venv\Scripts\python -m unittest discover -s tests -v
node --test tests/countdown.test.cjs
```

To preview the celebration, temporarily set `BIRTHDAY_DATE` to today's date (or a past date), restart, and reload. Restore the real date afterward. Never change your device clock for this test.
