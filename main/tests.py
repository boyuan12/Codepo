from django.test import Client, TestCase
from django.contrib.auth.models import User
from .models import Profile, Repository

# Create your tests here.
class RepositoryTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        User.objects.create_user(username="testing", password="testing")
        u = User.objects.get(username="testing")
        Profile(user_id=u.id, description="", organization="", location="", website="", avatar="").save()
        Repository(user_id=u.id, name="testing2", description="", status=1).save()

    def login(self):
        rv = self.client.post("/auth/login/", data={
            "username": "testing",
            "password": "testing",
            "deviceid": ""
        }, follow=True)

    def test_create_repo(self):
        self.login()
        rv = self.client.post("/new/", data={
            "name": "testing",
            "description": "",
            "status": "public"
        }, follow=True)
        assert b'testing' in rv.content
        assert b'master' in rv.content
        assert b'/' in rv.content

    def test_create_new_branch(self):
        self.login()
        rv = self.client.post("/new-branch/", data={
            "name": "testing_branch",
            "repo": "testing2"
        }, follow=True)
        assert b'testing_branch' in rv.content

