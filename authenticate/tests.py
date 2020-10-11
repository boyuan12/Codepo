from django.test import Client, TestCase
from time import sleep
import requests
import random
from string import ascii_letters
from django.contrib.auth.models import User
from .models import Verify
import os
# Create your tests here.

def random_str(n=5):
    return "".join([random.choice(ascii_letters) for i in range(n)])


class AuthenticationTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        User(username="hello", password="world").save()
        u = User.objects.get(username="hello")
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

        print(rv.content)
        assert b"Your account is successfully created, but please check your email to verify your account." in rv.content

        r = requests.get(f"https://api.testmail.app/api/json?apikey={os.getenv('TESTMAIL_API')}&namespace=5v6g6&pretty=true&livequery=true&limit=1&tag={tag}&headers=true").json()
        # print(r)
        code = r["emails"][0]["html"].split("Verification code: ")[1]
        # print(code)

        Verify.objects.get(id=code)


    # def test_verify_an_account(self):
    #     u = User.objects.get(username="hello")
    #     code = Verify.objects.get(user_id=u.id)

    #     rv = self.client.get(f"/auth/verify/{code}/", follow=True)

    #     print(rv.content)