from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage

import os

from main.models import Repository, Directory, File, Branch
import requests

from GitHubClone.settings import DEBUG

import boto3
import random
import string
import pathlib

from termcolor import colored
BASE_URL = "https://github-clone-dj.herokuapp.com"

def random_str(n):
    s = ""
    for i in range(n):
        s += random.choice(string.ascii_letters + string.digits)
    return s

def upload_s3(request):
    s3 = boto3.resource("s3", aws_access_key_id=os.getenv("S3_ACCESS_KEY_ID"), aws_secret_access_key=os.getenv("S3_SECRET_ACCESS_KEY_ID"))
    name = random_str(10)
    s3.Bucket('githubclone').put_object(Key=f"{name}.{pathlib.Path(request.FILES['file'].name).suffix}", Body=request.FILES["file"])
    return f"{name}.{pathlib.Path(request.FILES['file'].name).suffix}"

def get_s3(name):
    s3 = boto3.resource("s3", aws_access_key_id=os.getenv("S3_ACCESS_KEY_ID"), aws_secret_access_key=os.getenv("S3_SECRET_ACCESS_KEY_ID"))
    obj = s3.Object("githubclone", f"{name}")
    body = obj.get()['Body'].read()
    return body

# Create your views here.
# @login_required(login_url='/auth/login/')
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
        b = request.GET["b"]
    except:
        b = "master"
    # return HttpResponse(b)
    try:
        dir = Directory.objects.get(path="/" + url + "/", repo_id=r.id, branch=b)
    except Exception as e:
        if url == "/":
            dir = Directory.objects.get(path="/", repo_id=r.id, branch=b)
        else:
            p = url.split("/")
            del p[-1]
            print(p)
            if len(p) != 0:
                dir = Directory.objects.get(path="/"+"/".join(p)+"/", repo_id=r.id, branch=b)
            else:
                dir = Directory.objects.get(path="/", repo_id=r.id, branch=b)
    try:
        files = File.objects.filter(repo_id=r.id, directory_id=dir.id, branch=b)
        for f in files:
            print(colored(url.split("/")[len(url.split("/"))-1], "yellow"))
            if f.filename == url or f.filename == url.split("/")[len(url.split("/"))-1]:
                p = url.split("/")
                filename = p[-1]
                del p[-1]
                p = "/".join(p)
                print(p)
                if len(p) != 0:
                    d = Directory.objects.get(path="/"+p+"/", repo_id=r.id, branch=b)
                else:
                    d = Directory.objects.get(path="/", repo_id=r.id, branch=b)
                file = File.objects.get(repo_id=r.id, directory_id=d.id, filename=filename, branch=b)
                print(file.url)
                content = get_s3(file.url)
                return render(request, "repo/file.html", {
                    "repo": repo,
                    "content": content.decode("utf-8"),
                    "username": username
                })
    except Exception as e:
        print(colored(e, "cyan"))
        files = []
    try:
        directories = Directory.objects.filter(dir_id=dir.id, branch=b)
    except Exception as e:
        print(colored(e, "cyan"))
        directories = set()

    try:
        readme = File.objects.get(directory_id=dir.id, filename="README.md", branch=b)
        readme = get_s3(readme.url).decode("utf-8")
    except Exception as e:
        print(str(e))
        readme = None
    print(readme)
    # print(colored(directories, "cyan"))
    return render(request, "repo/repo.html", {
        "repo": repo,
        "files": files,
        "dirs": directories,
        "username": username,
        "readme": readme,
        "root": True if url == "/" else False,
        "branches": Branch.objects.filter(repo_id=r.id),
        "b": b
    })


@login_required(login_url='/auth/login/')
def upload(request, username, repo, url="/"):

    try:
        b = request.GET["b"]
    except:
        b = "master"

    if request.method == "POST":
        name = upload_s3(request)
        r = Repository.objects.get(user_id=request.user.id, name=repo).id
        if url == "/":
            d = Directory.objects.get(repo_id=r, path="/", branch=b).id
        else:
            d = Directory.objects.get(repo_id=r, path="/" + url + "/", branch=b).id
        f = File(repo_id=r, filename=request.FILES["file"].name, directory_id=d, url=name, branch=b)
        f.save()
        if url == "/":
            return HttpResponseRedirect(f"/repo/{username}/{repo}/{request.FILES['file'].name}")
        else:
            return HttpResponseRedirect(f"/repo/{username}/{repo}/{url}/{request.FILES['file'].name}")
    else:
        return render(request, "repo/upload.html", {
            "repo": repo,
            "username": username
        })


def create_folder(request, username, repo, url="/"):

    try:
        b = request.GET["b"]
    except:
        b = 'master'

    if request.method == "POST":
        r = Repository.objects.get(name=repo, user_id=request.user.id)
        if url == "/":
            root = Directory.objects.get(name="/", repo_id=r.id, branch=b)
            d = Directory(dir_id=root.id, repo_id=r.id, name=request.POST["name"], path="/"+request.POST["name"]+"/", branch=b)
            d.save()
            return HttpResponseRedirect(f"/repo/{username}/{repo}/{request.POST['name']}/")
        else:
            d = Directory.objects.get(path="/"+url+"/", branch=b)
            dir = Directory(dir_id=d.id, path="/"+url+"/"+request.POST["name"]+"/", repo_id=r.id, name=request.POST["name"], branch=b)
            dir.save()
            return HttpResponseRedirect(f"/repo/{username}/{repo}/{url}/{request.POST['name']}/")
            #return to the new dir
    else:
        return render(request, "repo/folder.html", {
            "repo": repo,
            "username": username
        })


def delete(request):
    try:
        b = request.GET["b"]
    except:
        b = 'master'

    url = request.GET["url"]
    url = url.split("/")
    username = url[1]
    repo = url[2]
    filename = url[len(url)-2]
    print(colored(filename, "cyan"))
    dir_path = "/"
    del url[0:3]
    del url[len(url)-1]
    for i in range(0, len(url)-1):
        dir_path += url[i] + "/"

    r = Repository.objects.get(user_id=request.user.id, name=repo)
    d = Directory.objects.get(repo_id=r.id, path=dir_path, branch=b)
    f = File.objects.get(repo_id=r.id, directory_id=d.id, filename=filename)
    f.delete()

    return HttpResponse(dir_path)

def delete_folder(request):
    path = request.GET["path"]