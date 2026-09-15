import re
import unittest
from app import create_app


class BirthdayAppTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app({'TESTING': True, 'SECRET_KEY': 't' * 32, 'SITE_PASSWORD': 'our-secret', 'SESSION_COOKIE_SECURE': False})
        self.client = self.app.test_client()

    def token(self):
        response = self.client.get('/login')
        return re.search(r'name="csrf_token" value="([^"]+)"', response.text).group(1)

    def login(self):
        return self.client.post('/login', data={'csrf_token': self.token(), 'password': 'our-secret'})

    def test_private_routes_redirect(self):
        for route in ['/', '/time', '/photos/anything.jpg']:
            self.assertEqual(self.client.get(route).status_code, 302)

    def test_login_logout_and_content(self):
        self.assertEqual(self.login().status_code, 302)
        page = self.client.get('/')
        self.assertEqual(page.status_code, 200)
        self.assertIn('2026-12-05T00:00:00+05:30', page.text)
        self.assertNotIn('our-secret', page.text)
        self.assertEqual(page.headers['Cache-Control'], 'no-store')
        token = re.search(r'name="csrf_token" value="([^"]+)"', page.text).group(1)
        self.client.post('/logout', data={'csrf_token': token})
        self.assertEqual(self.client.get('/').status_code, 302)

    def test_csrf_and_wrong_password(self):
        self.assertEqual(self.client.post('/login', data={'password': 'our-secret'}).status_code, 400)
        result = self.client.post('/login', data={'password': 'wrong', 'csrf_token': self.token()})
        self.assertIn("our secret", result.text)
        self.assertEqual(self.client.get('/').status_code, 302)

    def test_throttling(self):
        token = self.token()
        for _ in range(10):
            self.client.post('/login', data={'password': 'wrong', 'csrf_token': token})
        self.assertEqual(self.client.post('/login', data={'password': 'wrong', 'csrf_token': token}).status_code, 429)

    def test_photo_traversal(self):
        self.login()
        self.assertEqual(self.client.get('/photos/../.env').status_code, 404)

    def test_time_endpoint(self):
        self.login()
        self.assertTrue(self.client.get('/time').json['now'].endswith('+00:00'))


if __name__ == '__main__':
    unittest.main()
