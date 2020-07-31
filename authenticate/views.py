from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from main.models import Profile, Follows
from django.http import HttpResponseRedirect, HttpResponse

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

        p = Profile(user_id=User.objects.get(username=username).id, description="", organization="", location="", website="", avatar="https://iupac.org/wp-content/uploads/2018/05/default-avatar.png")
        p.save()

        login(request, User.objects.get(username=username))

        request.session["img"] = Profile.objects.get(user_id=request.user.id).avatar

        return HttpResponseRedirect("/")

    else:
        return render(request, "authenticate/register.html")


def login_view(request):

    if request.method == "POST":

        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
        else:
            user = authenticate(email=username, password=password)
            if user is not None:
                login(request,user)
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