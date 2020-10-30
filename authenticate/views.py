from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from main.models import Profile, Follows
from django.http import HttpResponseRedirect, HttpResponse
from .models import Verify, TwoFAToken, TwoFA, AuthorizedDevice
from mail import send_mail
from twilio.rest import Client
import os
import random
from string import digits
import datetime
import httpagentparser


def random_2fa_code(n=6):
    return "".join([random.choice(digits) for i in range(n)])

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
client = Client(account_sid, auth_token)

# Create your views here.
def register(request):

    if request.method == "POST":

        email = request.POST["email"]
        username = request.POST["username"]
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        f_name = request.POST["f_name"]
        l_name = request.POST["l_name"]

        try:
            User.objects.get(username=username)
            return HttpResponse("error")
        except:
            try:
                User.objects.get(email=email)
                return HttpResponse("same email")
            except:
                pass

        user = User.objects.create_user(username=username, email=email, password=password, first_name=f_name, last_name=l_name)
        user.save()

        user = User.objects.get(username=username)

        p = Profile(user_id=User.objects.get(username=username).id, description="", organization="", location="", website="", avatar="https://iupac.org/wp-content/uploads/2018/05/default-avatar.png")
        p.save()

        Verify(user_id=user.id, code=0).save()
        code = Verify.objects.get(user_id=user.id, code=0).id

        send_mail(email, "Verify your account", f"Hello! Please click on this link to verify your email address: <a href='http://127.0.0.1:8000/auth/verify/{str(code)}'>http://127.0.0.1:8000/auth/verify/{str(code)}</a> Verification code: {str(code)}")

        return HttpResponse("Your account is successfully created, but please check your email to verify your account.")

    else:
        return render(request, "authenticate/register.html")


def login_view(request):
    h = httpagentparser.detect(request.headers["User-Agent"])
    print(h)
    if request.method == "POST":

        username = request.POST["username"]
        password = request.POST["password"]

        user1 = authenticate(username=username, password=password)

        if user1 is not None:
            try:
                Verify.objects.get(user_id=user1.id, code=0)
                return HttpResponse("Your account is successfully created, but please check your email to verify your account.")
            except:
                try:
                    AuthorizedDevice(user_id=user1.id, )
                except:
                    pass
                login(request, user1)

        else:
            try:
                user2 = User.objects.get(email=request.POST["username"])
            except:
                return HttpResponse("invalid lol")

            user2 = authenticate(username=user2.username, password=request.POST["password"])

            if user2 is not None:
                try:
                    Verify.objects.get(user_id=user2.id, code=0)
                    return HttpResponse("Your account is successfully created, but please check your email to verify your account.")
                except Exception as e:
                    login(request, user2)
            else:
                return HttpResponse("invalid")

        request.session["img"] = Profile.objects.get(user_id=request.user.id).avatar

        try:
            return HttpResponseRedirect(request.GET["next"])
        except:
            return HttpResponseRedirect("/")

    else:
        return render(request, "authenticate/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect("/")


def verify_account(request, code):
    try:
        Verify.objects.get(id=code, code=0)
        Verify.objects.get(id=code, code=0).delete()
    except:
        return HttpResponse("Invalid code")

    return HttpResponseRedirect("/auth/login/")


def forgot_password(request):
    if request.method == "POST":
        try:
            try:
                user = User.objects.get(username=request.POST["username"])
            except:
                try:
                    user = User.objects.get(email=request.POST["username"])
                except:
                    return HttpResponse("Invalid username or email")

            Verify(user_id=user.id, code=1).save()
            v = Verify.objects.get(user_id=user.id, code=1)
            print(v, user.email)
            send_mail(user.email, "Code for change your password", f"Hello! Please click on this link to change your password: <a href='http://127.0.0.1:8000/auth/forgot-password/{str(v.id)}/'>http://127.0.0.1:8000/auth/forgot-password/{str(v.id)}</a> Forgot Password Code: {str(v.id)}")
            return HttpResponse("Success, please check your email")

        except:
            return HttpResponse("Invalid username")
    else:
        return render(request, "authenticate/forgot-password.html")


def reset_password(request, code):
    if request.method == "POST":
        v = Verify.objects.get(id=code, code=1)
        user = User.objects.get(id=v.user_id)
        user.set_password(request.POST["password"])
        user.save()
        v.delete()

        return HttpResponseRedirect("/auth/login/")

    else:
        try:
            v = Verify.objects.get(id=code, code=1)
            user = User.objects.get(id=v.user_id)
            return render(request, "authenticate/reset-password.html", {
                "username": user.username
            })
            # Verify.objects.get(id=code, code=1).delete()
        except Exception as e:
            return HttpResponse("Invalid code")


@login_required(login_url="/auth/login/")
def twofa(request):
    if request.method == "POST":
        country_code = request.POST["countryCode"]
        phone_number = request.POST["phoneNumber"]
        code = random_2fa_code()
        client.messages.create(from_='+19162800623', body=f'Your 2-Factor Authentication code for GitHub Clone: {code}', to=f'+{country_code}{phone_number}')
        TwoFAToken(user_id=request.user.id, code=code, phone=f'+{country_code}{phone_number}').save()
        t = datetime.datetime.now() + datetime.timedelta(minutes=3)
        request.session["re2fa"] = (t.year, t.month, t.day, t.hour,t.minute, t.second)
        return HttpResponse("success")
    else:
        seconds = 0
        try:
            time = request.session["re2fa"]
            time = datetime.datetime(year=time[0], month=time[1], day=time[2], hour=time[3], minute=time[4], second=time[5])
            current = datetime.datetime.now()
            difference = current-time
            left = divmod(difference.days * (24 * 60 * 60) + difference.seconds, 60)
            seconds = left[0] * 60 + left[1]
        except:
            pass
        if seconds > 0:
            seconds = 0
        return render(request, "authenticate/phone_verify.html", {
            "seconds": ["a" for i in range(seconds * -1)]
        })


def twofa_verify(request):
    if request.method == "POST":
        try:
            t = TwoFAToken.objects.get(code=request.POST["code"])
            try:
                r = request.GET["next"]
                return HttpResponseRedirect(r)
            except Exception as e:
                print(e)
                pass
            TwoFA(user_id=request.user.id, phone=t.phone).save()
            return HttpResponse("Successfully Verified.")
        except Exception as e:
            print(e)
            return HttpResponse("Invalid code")
    else:
        return render(request, "authenticate/phone_code.html")
