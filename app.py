"""One small, private birthday keepsake. Run with python serve.py."""
import hmac
import json
import os
import secrets
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

from dotenv import load_dotenv
from flask import Flask, abort, jsonify, redirect, render_template, request, send_from_directory, session, url_for

ROOT = Path(__file__).resolve().parent


def create_app(test_config=None):
    load_dotenv(ROOT / '.env')
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=os.getenv('SECRET_KEY'),
        SITE_PASSWORD=os.getenv('SITE_PASSWORD'),
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax',
        SESSION_COOKIE_SECURE=os.getenv('COOKIE_SECURE', 'true').lower() == 'true',
        PERMANENT_SESSION_LIFETIME=timedelta(days=7),
        MAX_CONTENT_LENGTH=8192,
        FIANCE_NAME=os.getenv('FIANCE_NAME', 'My love'),
        YOUR_NAME=os.getenv('YOUR_NAME', 'Your forever person'),
        BIRTHDAY_DATE=os.getenv('BIRTHDAY_DATE', '2026-12-05'),
        BIRTHDAY_TIMEZONE=os.getenv('BIRTHDAY_TIMEZONE', 'Asia/Kolkata'),
    )
    if test_config:
        app.config.update(test_config)
    if not app.config['SECRET_KEY'] or len(app.config['SECRET_KEY']) < 32:
        raise RuntimeError('Set SECRET_KEY to a random value of at least 32 characters in .env.')
    if not app.config['SITE_PASSWORD'] or app.config['SITE_PASSWORD'] == 'replace-with-your-shared-secret':
        raise RuntimeError('Set your own SITE_PASSWORD in .env.')
    target = datetime.strptime(app.config['BIRTHDAY_DATE'], '%Y-%m-%d').replace(tzinfo=ZoneInfo(app.config['BIRTHDAY_TIMEZONE']))
    content = json.loads((ROOT / 'content.json').read_text(encoding='utf-8'))
    # A global rolling limit for this single-process, single-password personal app.
    # Do not trust client-supplied forwarding headers for rate-limit identities.
    attempts = []
    lock = threading.Lock()

    @app.before_request
    def protect():
        if request.endpoint not in ('login', 'static', 'health') and not session.get('authenticated'):
            return redirect(url_for('login'))
        if request.method == 'POST':
            token = request.form.get('csrf_token', '')
            if not token or not hmac.compare_digest(token, session.get('csrf_token', '')):
                abort(400, 'This page expired. Reload it and try again.')

    @app.after_request
    def headers(response):
        response.headers['Cache-Control'] = 'no-store'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['Referrer-Policy'] = 'no-referrer'
        response.headers['Content-Security-Policy'] = "default-src 'self'; img-src 'self' https: data:; style-src 'self'; script-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'"
        return response

    @app.context_processor
    def common():
        session.setdefault('csrf_token', secrets.token_urlsafe(32))
        return dict(name=app.config['FIANCE_NAME'], sender=app.config['YOUR_NAME'], csrf_token=session['csrf_token'])

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if session.get('authenticated'):
            return redirect(url_for('index'))
        error, status = None, 200
        if request.method == 'POST':
            with lock:
                now = time.monotonic()
                attempts[:] = [x for x in attempts if now - x < 300]
                if len(attempts) >= 10:
                    error, status = 'A little pause, love. Please try again in five minutes.', 429
                elif hmac.compare_digest(request.form.get('password', '').encode(), app.config['SITE_PASSWORD'].encode()):
                    attempts.clear()
                    session.clear()
                    session.update(authenticated=True, csrf_token=secrets.token_urlsafe(32))
                    session.permanent = True
                    return redirect(url_for('index'))
                else:
                    attempts.append(now)
                    error = "That isn't our secret. Give it another try."
        return render_template('login.html', error=error), status

    @app.get('/')
    def index():
        return render_template('index.html', content=content, date_label=target.strftime('%d %B %Y').lstrip('0'), config_data={
            'target': target.isoformat(), 'serverNow': datetime.now(ZoneInfo('UTC')).isoformat(),
            'name': app.config['FIANCE_NAME'], 'fortunes': content['fortunes'],
        })

    @app.get('/time')
    def server_time():
        return jsonify(now=datetime.now(ZoneInfo('UTC')).isoformat())

    @app.post('/logout')
    def logout():
        session.clear()
        return redirect(url_for('login'))

    @app.get('/photos/<path:filename>')
    def photos(filename):
        return send_from_directory(ROOT / 'private_photos', filename)

    @app.get('/health')
    def health():
        return {'status': 'ok'}

    return app
