from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
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
    print(colored(url, "red"))
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

    try:
        dir = Directory.objects.get(path="/" + url + "/", repo_id=r.id)
    except Exception as e:
        if url == "/":
            dir = Directory.objects.get(path="/", repo_id=r.id)
        else:
            p = url.split("/")
            del p[-1]
            print(p)
            if len(p) != 0:
                dir = Directory.objects.get(path="/"+"/".join(p)+"/")
            else:
                dir = Directory.objects.get(path="/")
    try:
        files = File.objects.filter(repo_id=r.id, directory_id=dir.id)
        for f in files:
            print(colored(url.split("/")[len(url.split("/"))-1], "yellow"))
            if f.filename == url or f.filename == url.split("/")[len(url.split("/"))-1]:
                p = url.split("/")
                filename = p[-1]
                del p[-1]
                p = "/".join(p)
                print(p)
                if len(p) != 0:
                    d = Directory.objects.get(path="/"+p+"/")
                else:
                    d = Directory.objects.get(path="/")
                file = File.objects.get(repo_id=r.id, directory_id=d.id, filename=filename)
                print(file.url)
                r = requests.get(file.url)
                return render(request, "repo/file.html", {
                    "repo": repo,
                    "content": r.text,
                    "username": username
                })
    except Exception as e:
        print(colored(e, "cyan"))
        files = []
    try:
        directories = Directory.objects.filter(dir_id=dir.id)
    except Exception as e:
        print(colored(e, "cyan"))
        directories = set()
    # print(colored(directories, "cyan"))
    return render(request, "repo/repo.html", {
        "repo": repo,
        "files": files,
        "dirs": directories,
        "username": username
    })




@login_required(login_url='/auth/login/')
def upload(request, username, repo, url="/"):
    print(url)
    try:
        request.GET["url"]
    except Exception as e:
        print(colored(e, "cyan"))
        return render(request, "repo/upload.html", {
            "repo": repo,
            "username": username
        })
    r = Repository.objects.get(user_id=request.user.id, name=repo).id
    if url == "/":
        d = Directory.objects.get(repo_id=r, path="/").id
    else:
        d = Directory.objects.get(repo_id=r, path="/" + url + "/").id
    f = File(repo_id=r, filename=request.GET["filename"], directory_id=d, url=request.GET["url"])
    f.save()
    return JsonResponse(message="success")


def create_folder(request, username, repo, url="/"):
    if request.method == "POST":
        r = Repository.objects.get(name=repo, user_id=request.user.id)
        if url == "/":
            root = Directory.objects.get(name="/", repo_id=r.id)
            d = Directory(dir_id=root.id, repo_id=r.id, name=request.POST["name"], path="/"+request.POST["name"]+"/")
            d.save()
            return HttpResponseRedirect(f"/repo/{username}/{repo}/{request.POST['name']}/")
        else:
            d = Directory.objects.get(path="/"+url+"/")
            dir = Directory(dir_id=d.id, path="/"+url+"/"+request.POST["name"]+"/", repo_id=r.id, name=request.POST["name"])
            dir.save()
            return HttpResponseRedirect(f"/repo/{username}/{repo}/{url}/{request.POST['name']}/")
            #return to the new dir
    else:
        return render(request, "repo/folder.html", {
            "repo": repo,
            "username": username
        })