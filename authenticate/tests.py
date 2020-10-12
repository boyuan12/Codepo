from django.test import Client, TestCase
from time import sleep
import requests
import random
from string import ascii_letters
from django.contrib.auth.models import User
from .models import Verify
from main.models import Profile
import os
# Create your tests here.

def random_str(n=5):
    return "".join([random.choice(ascii_letters) for i in range(n)])


class AuthenticationTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        # User().save()
        User.objects.create_user(username="hello", password="world", email="5v6g6.forgotPassword@inbox.testmail.app")
        u = User.objects.get(username="hello")
        Profile(user_id=u.id, description="", organization="", location="", website="", avatar="").save()
        Verify(user_id=u.id, code=0).save()

    def test_register_login_and_check_verify(self):
        tag = random_str()
        rv = self.client.post("/auth/register/", data={
            "email": f"5v6g6.{tag}@inbox.testmail.app",
            "username": "abc",
            "password": "abc",
            "confirmation": "abc",
            "f_name": "abc",
            "l_name": "abc"
        }, follow=True)

        rv = self.client.post("/auth/login/", data={
            "username": "abc",
            "password": "abc"
        }, follow=True)

        # print(rv.content)
        assert b"Your account is successfully created, but please check your email to verify your account." in rv.content

        r = requests.get(f"https://api.testmail.app/api/json?apikey={os.getenv('TESTMAIL_API')}&namespace=5v6g6&pretty=true&livequery=true&limit=1&tag={tag}&headers=true").json()
        # print(r)
        code = r["emails"][0]["html"].split("Verification code: ")[1]
        # print(code)

        Verify.objects.get(id=code)

    def test_verify(self):
        u = User.objects.get(username="hello")
        v = Verify.objects.get(user_id=u.id, code=0)
        rv = self.client.get(f"/auth/verify/{str(v.id)}/", follow=True)
        assert b'Login' in rv.content

        rv = self.client.post("/auth/login/", data={
            "username": "hello",
            "password": "world"
        }, follow=True)
        assert b'Repositories' in rv.content

    def test_forgot_password(self):
        tag = random_str()
        User.objects.create_user(username="test2", password="test2", email=f"5v6g6.{tag}@inbox.testmail.app")
        user = User.objects.get(username="test2")
        Profile(user_id=user.id, description="", organization="", location="", website="", avatar="").save()

        rv = self.client.post("/auth/forgot-password/", data={
            "username": "test2"
        }, follow=True)
        print(rv.content)

        r = requests.get(f"https://api.testmail.app/api/json?apikey={os.getenv('TESTMAIL_API')}&namespace=5v6g6&pretty=true&livequery=true&limit=1&tag={tag}&headers=true").json()
        code = r["emails"][0]["html"].split("Forgot Password Code: ")[1]
        print(code)

        rv = self.client.post(f"/auth/forgot-password/{code}/", {
            "password": "new-password"
        }, follow=True)

        assert b"Login" in rv.content

        rv = self.client.post(f"/auth/login/", {
            "username": "test2",
            "password": "new-password"
        }, follow=True)

        assert b"Repositories" in rv.content
    # def test_verify_an_account(self):
    #     u = User.objects.get(username="hello")
    #     code = Verify.objects.get(user_id=u.id)

    #     rv = self.client.get(f"/auth/verify/{code}/", follow=True)

    #     print(rv.content)