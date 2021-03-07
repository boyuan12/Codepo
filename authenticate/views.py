from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from main.models import Profile, Follows
from django.http import HttpResponseRedirect, HttpResponse
from .models import Verify, TwoFAToken, TwoFA, AuthorizedDevice, TwoFAUsage
from mail import send_mail
from twilio.rest import Client
import os
import random
from string import digits
import datetime
import httpagentparser
from termcolor import colored
from GitHubClone.settings import DEBUG
import requests


if DEBUG:
    BASE_URL = "http://127.0.0.1:8000"
else:
    BASE_URL = "https://github-clone-dj.herokuapp.com"


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

HEROKU_CLIENT_ID = os.getenv("HEROKU_CLIENT_ID")
HEROKU_CLIENT_SECRET = os.getenv("HEROKU_CLIENT_SECRET")

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

        send_mail(email, "Verify your account", f"Hello! Please click on this link to verify your email address: <a href='{BASE_URL}/auth/verify/{str(code)}'>{BASE_URL}/auth/verify/{str(code)}</a> Verification code: {str(code)}")

        return HttpResponse("Your account is successfully created, but please check your email to verify your account.")

    else:
        return render(request, "authenticate/register.html")


def login_view(request):
    # h = httpagentparser.detect(request.headers["User-Agent"])
    # print(h)
    print(request.COOKIES)

    if request.method == "POST":

        device_id = request.POST["deviceid"]
        username = request.POST["username"]
        password = request.POST["password"]

        try:
            r = request.GET["next"]
        except:
            r = "/"

        user1 = authenticate(username=username, password=password)

        if user1 is not None:
            try:
                Verify.objects.get(user_id=user1.id, code=0)
                return HttpResponse("Your account is successfully created, but please check your email to verify your account. Click if you need to <a href='/auth/verify/again/'>send the verification mail again</a>.")
            except:
                try:
                    TwoFAUsage.objects.get(user_id=user1.id)
                    try:
                        AuthorizedDevice.objects.get(user_id=user1.id, id=device_id)
                        print(device_id)
                    except Exception as e:
                        print(str(e), "red")
                        request.session["2fa_user_id"] = user1.id
                        request.session["r"] = r
                        print(request.session)
                        return HttpResponseRedirect("/auth/2fa/devices/verify/")
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
                    try:
                        TwoFAUsage.objects.get(user_id=user1.id)
                        try:
                            AuthorizedDevice.objects.get(user_id=user2.id, id=device_id)
                            print(colored("2", "red"))
                        except Exception as e:
                            print(colored(str(e), "yellow"))
                            request.session["2fa_user_id"] = user2.id
                            request.session["r"] = r
                            return HttpResponseRedirect("/auth/2fa/devices/verify/")
                    except:
                        pass

                    login(request, user2)
            else:
                return HttpResponse("invalid")

        request.session["img"] = Profile.objects.get(user_id=request.user.id).avatar

        # return render(request, "authenticate/redirect.html", {"route": r, "deviceid": "hihihi-1234-l14m"})
        return HttpResponseRedirect(r)

    else:
        print(request.session.get("deviceid"), "blue")
        if request.session.get("deviceid") is not None:
            return render(request, "authenticate/redirect.html", {
                "route": request.session.get("r"), 
                "deviceid": request.session.get("deviceid")
            })

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
            
            send_mail(user.email, "Code for change your password", f"Hello! Please click on this link to change your password: <a href='{BASE_URL}/auth/forgot-password/{str(v.id)}/'>{BASE_URL}/auth/forgot-password/{str(v.id)}</a> Forgot Password Code: {str(v.id)}")
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
            TwoFAUsage(user_id=request.user.id).save()
            return HttpResponse("Successfully Verified.")
        except Exception as e:
            print(e)
            return HttpResponse("Invalid code")
    else:
        return render(request, "authenticate/phone_code.html")


def twofa_device_verify(request):
    if request.method == "POST":
        print(request.session)
        try:
            t = TwoFAToken.objects.get(code=request.POST["code"])
            user_id = t.user_id
            t.delete()
        except:
            return HttpResponse("Invalid code")
        
        u = User.objects.get(id=user_id)
        login(request, u)

        request.session["img"] = Profile.objects.get(user_id=request.user.id).avatar

        AuthorizedDevice(user_id=request.user.id).save()
        request.session["deviceid"] = str(AuthorizedDevice.objects.filter(user_id=request.user.id)[::-1][0].id)

        return HttpResponseRedirect("/auth/login/")


    else:
        try:
            t = TwoFA.objects.get(user_id=request.session.get("2fa_user_id"))
            code = random_2fa_code()
            TwoFAToken(user_id=request.session.get("2fa_user_id"), code=code, phone="").save()
            client.messages.create(from_='+19162800623', body=f'Your 2-Factor Authentication code for GitHub Clone: {code}', to=t.phone)
            print(t.phone)
            way = "a SMS message to which you registered"
        except Exception as e:
            print(e)
            u = User.objects.get(id=request.session.get("2fa_user_id"))
            code = random_2fa_code()
            TwoFAToken(user_id=request.session.get("2fa_user_id"), code=code, phone="").save()
            send_mail(u.email, "Are you really you?", f"Your 2FA code for GitHub Clone is: {code}")
            way = "an email to which you register"
        
        return render(request, "authenticate/2fa_device.html", {
            "way": way,
        })


@login_required(login_url="/auth/login/")
def twofa_email(request):

    try:
        TwoFAUsage.objects.get(user_id=request.user.id)
    except:
        TwoFAUsage(user_id=request.user.id).save()

    return HttpResponseRedirect("/profile/")


@login_required(login_url="/auth/login/")
def twofa_opt_out(request):

    TwoFAToken.objects.filter(user_id=request.user.id).delete()
    TwoFA.objects.filter(user_id=request.user.id).delete()
    TwoFAUsage.objects.filter(user_id=request.user.id).delete()

    return HttpResponseRedirect("/profile/")


def resend_verification_email(request):
    Verify(user_id=request.user.id, code=1).save()
    v = Verify.objects.get(user_id=request.user.id, code=1)
    
    send_mail(request.user.email, "Code for change your password", f"Hello! Please click on this link to change your password: <a href='{BASE_URL}/auth/forgot-password/{str(v.id)}/'>{BASE_URL}/auth/forgot-password/{str(v.id)}</a> Forgot Password Code: {str(v.id)}")
    return HttpResponse("Success, please check your email")


def login_with_heroku(request):
    if request.GET.get("next"):
        request.session["h_next"] = request.GET.get("next")
    return HttpResponseRedirect(f"https://id.heroku.com/oauth/authorize?client_id={HEROKU_CLIENT_ID}&response_type=code&scope=global&state=abcd")


def heroku_callback(request):
    data = requests.post("https://id.heroku.com/oauth/token", data={
        "grant_type": "authorization_code",
        "code": request.GET.get("code"),
        "client_secret": HEROKU_CLIENT_SECRET
    })
    
    try:
        request.session["HEROKU_ACCESS_TOKEN"] = data.json()["access_token"]
    except KeyError:
        print(data.json())

    if request.session.get("h_next"):
        return HttpResponseRedirect(request.session.get("h_next"))
    return HttpResponseRedirect("/")
