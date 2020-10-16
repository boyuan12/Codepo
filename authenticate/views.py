from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from main.models import Profile, Follows
from django.http import HttpResponseRedirect, HttpResponse
from .models import Verify
from mail import send_mail


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

    if request.method == "POST":

        username = request.POST["username"]
        password = request.POST["password"]

        user1 = authenticate(username=username, password=password)

        if user1 is not None:
            try:
                Verify.objects.get(user_id=user1.id, code=0)
                return HttpResponse("Your account is successfully created, but please check your email to verify your account.")
            except:
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