from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage

import os

from main.models import Repository, Directory, File
import requests

from GitHubClone.settings import DEBUG

from termcolor import colored
BASE_URL = "https://github-clone-dj.herokuapp.com"


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

    if url.count("/") < 2 and url != "/":
        url = url.split("/")[0]
        directory_id = Directory.objects.get(repo_id=r.id, name="/").id
        file = File.objects.get(directory_id=directory_id, filename=url)
        r = requests.get(file.url)
        return render(request, "repo/file.html", {
            "content": r.text,
            "repo": repo,
            "username": username
        })

    directory_id = Directory.objects.get(repo_id=r.id, name=url).id
    files = File.objects.filter(directory_id=directory_id)

    print(files)

    if url == "upload/":
        return render(request, "repo/upload.html", {
            "repo": repo,
            "username": username
        })

    return render(request, "repo/repo.html", {
        "files": files,
        "repo": repo,
        "username": username
    })


@login_required(login_url='/auth/login/')
def upload(request, username, repo, url="/"):
    try:
        request.GET["url"]
    except Exception as e:
        print(e)
        return render(request, "repo/upload.html", {
            "repo": repo,
            "username": username
        })
    print(colored(request.user.id, "yellow"))
    r = Repository.objects.get(user_id=request.user.id, name=repo).id
    print(r)
    d = Directory.objects.get(repo_id=r, name=url).id
    print(d)
    f = File(repo_id=r, filename=request.GET["filename"], directory_id=d, url=request.GET["url"])
    f.save()
    return render(request, "repo/uploaded.html", {
        "repo": repo,
        "username": username
    })