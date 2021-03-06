import json
from project.tests.base import BaseTestCase
from project import db
from project.api.models import User


class TestUserService(BaseTestCase):
    def test_users(self):
        response = self.client.get('/ping')
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertIn('pong', data['message'])
        self.assertIn('success', data['status'])

    def test_add_user(self):
        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps(dict(username='cnych',
                                     email='qikqiak@gmail.com')),
                content_type='application/json',
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 201)
            self.assertIn('qikqiak@gmail.com was added', data['message'])
            self.assertEqual('success', data['status'])

    def test_add_user_invalid_json(self):
        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps(dict()),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid payload', data['message'])
            self.assertEqual('fail', data['status'])

    def test_add_user_invalid_json_keys(self):
        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps(dict(email='qikqiak@gmail.com')),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid payload', data['message'])
            self.assertEqual('fail', data['status'])

        with self.client:
            response = self.client.post(
                '/users',
                data=json.dumps(dict(username='cnych')),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Invalid payload', data['message'])
            self.assertEqual('fail', data['status'])

    def test_add_user_duplicate_user(self):
        with self.client:
            self.client.post(
                '/users',
                data=json.dumps(dict(
                    username='cnych',
                    email='qikqiak@gmail.com'
                )),
                content_type='application/json'
            )
            response = self.client.post(
                '/users',
                data=json.dumps(dict(
                    username='cnych',
                    email='qikqiak@gmail.com'
                )),
                content_type='application/json'
            )
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Sorry. That email already exists.', data['message'])
            self.assertEqual('fail', data['status'])

    def test_get_user(self):
        user = User(username='cnych', email='qikqiak@gmail.com')
        db.session.add(user)
        db.session.commit()
        with self.client:
            response = self.client.get('/users/%d' % user.id)
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertTrue('created_at' in data['data'])
            self.assertEqual('cnych', data['data']['username'])
            self.assertEqual('qikqiak@gmail.com', data['data']['email'])
            self.assertEqual('success', data['status'])

    def test_get_user_no_id(self):
        with self.client:
            response = self.client.get('/users/xxx')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 400)
            self.assertIn('Param id error', data['message'])
            self.assertEqual('fail', data['status'])

    def test_get_user_incorrect_id(self):
        with self.client:
            response = self.client.get('/users/-1')
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 404)
            self.assertIn('User does not exist', data['message'])
            self.assertEqual('fail', data['status'])

    def test_main_no_users(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'No users!', response.data)

    def test_main_with_users(self):
        def add_user(username, email):
            self.client.post(
                '/',
                data=dict(username=username, email=email),
                follow_redirects=True
            )

        add_user('cnych', 'icnych@gmail.com')
        add_user('qikqiak', 'qikqiak@gmail.com')
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'All Users', response.data)
        self.assertNotIn(b'No users!', response.data)
        self.assertIn(b'cnych', response.data)
        self.assertIn(b'qikqiak', response.data)

    def test_main_add_user(self):
        with self.client:
            response = self.client.post(
                '/',
                data=dict(username='cnych', email='cnych@gmail.com'),
                follow_redirects=True
            )
            self.assertEqual(response.status_code, 200)
            self.assertIn(b'All Users', response.data)
            self.assertNotIn(b'No users!', response.data)
            self.assertIn(b'cnych', response.data)
