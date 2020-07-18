from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
import os
import GitHubClone.settings as settings
from django.contrib.auth.decorators import login_required

from .models import Repository, File, Directory

# Create your views here.
@login_required(login_url='/auth/login/')
def index(request):
    repos = Repository.objects.filter(user_id=request.user.id)
    return render(request, "main/index.html", {
        "repos": repos
    })


@login_required(login_url='/auth/login/')
def new(request):
    if request.method == "POST":

        status = None
        if request.POST["status"] == "public":
            status = 0
        else:
            status = 1

        r = Repository(user_id=request.user.id, name=request.POST["name"], description=request.POST["description"], status=status)
        r.save()

        d = Directory(repo_id=Repository.objects.get(user_id=request.user.id, name=request.POST["name"], description=request.POST["description"], status=status).id, name="/", dir_id=0, path="/")
        d.save()

        return HttpResponseRedirect(f"/repo/{request.user.username}/{request.POST['name']}/")

    else:
        return render(request, "main/new.html")