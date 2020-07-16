from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage

import os

from main.models import Repository, Directory, File
import requests

from GitHubClone.settings import DEBUG

BASE_URL = "https://github-clone-dj.herokuapp.com"

def handle_uploaded_file(f):
    with open('repo/static/repo/'+f.name, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)


# Create your views here.
@login_required(login_url='/auth/login/')
def repo(request, username, repo, url="/"):
    # check whether it's valid
    # get user id
    try:
        user_id = User.objects.get(username=username).id
    except:
        return HttpResponse("404 Not Found")

    try:
        r = Repository.objects.get(user_id=user_id, name=repo)
    except:
        return HttpResponse("404")

    if r.status == 1 and r.user_id != request.user.id:
        return HttpResponse("403")

    directory_id = Directory.objects.get(repo_id=r.id, name=url).id
    files = File.objects.filter(directory_id=directory_id)

    if url == "upload/":
        return render(request, "repo/upload.html")

    return render(request, "repo/repo.html", {
        "files": files,
        "repo": repo
    })


@login_required(login_url='/auth/login/')
def upload(request, username, repo, url="/"):
    if request.method == "POST":
        handle_uploaded_file(request.FILES["file"])
        r = Repository(user_id=request.user.id, name=repo).id
        d = Directory(repo_id=r, name=url).id
        if DEBUG == False:
            url = requests.get(f"https://github-clone-cdn.glitch.me/scrape?url={BASE_URL}/static/repo/{request.FILES['file'].name}").json()
            f = File(repo_id=r, filename=request.FILES["file"].name, directory_id=d, url=url["url"])
        return render(request, "repo/uploaded.html")
    else:
        return render(request, "repo/upload.html")
