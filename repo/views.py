from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect, Http404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage
import os
from main.models import Repository, Directory, File, Branch, Star, Commit, Commit_File
import requests
from GitHubClone.settings import DEBUG
import boto3
import random
import string
import pathlib
from termcolor import colored
import uuid



BASE_URL = "https://github-clone-dj.herokuapp.com"

s3 = boto3.resource("s3", aws_access_key_id=os.getenv("S3_ACCESS_KEY_ID"), aws_secret_access_key=os.getenv("S3_SECRET_ACCESS_KEY_ID"))

def random_str(n):
    s = ""
    for i in range(n):
        s += random.choice(string.ascii_letters + string.digits)
    return s

def upload_s3(request):
    name = random_str(10)
    s3.Bucket('githubclone').put_object(Key=f"{name}{pathlib.Path(request.FILES['file'].name).suffix}", Body=request.FILES["file"], ACL="public-read")
    return f"{name}{pathlib.Path(request.FILES['file'].name).suffix}"

def get_s3(name):
    obj = s3.Object("githubclone", f"{name}")
    body = obj.get()['Body'].read()
    return body

def dirize(s):
    path = ""
    for i in s:
        if i == "":
            path += "/"
        else:
            path += i + "/"

    return path
# Create your views here.
# @login_required(login_url='/auth/login/')
def repo(request, username, repo, path="/"):
    try:
        b = request.GET["b"]
    except:
        b = "master"

    user = User.objects.get(username=username)
    r = Repository.objects.get(name=repo, user_id=user.id)
    branches = Branch.objects.filter(repo_id=r.id)

    if "/" not in path or path != "/":
        path = "/" + path + "/"

    forked = None

    if r.fork != None:
        forked = Repository.objects.get(id=r.fork)
        forked_username = User.objects.get(id=forked.user_id).username
        forked = f"Forked from {forked_username}/{forked.name}"

    # check for directory or file using path
    try:
        d = Directory.objects.get(repo_id=r.id, path=path, branch=b)
        dirs = Directory.objects.filter(repo_id=r.id, subdir=d.id, branch=b)
        print(dirs)
        files = File.objects.filter(repo_id=r.id, subdir=d.id, branch=b)
        return render(request, "repo/repo.html", {
            "files": files,
            "dirs": dirs,
            "branches": branches,
            "b": b,
            "repo": repo,
            "username": username,
            "forked": forked
        })
    except:
        try:
            f = File.objects.get(repo_id=r.id, path=path, branch=b)
        except Exception as e:
            print(e)
            return HttpResponse("Not Found")
        content = get_s3(f.url)
        try:
            return render(request, "repo/file.html", {
                "content": content.decode("utf-8"),
                "repo": repo,
                "username": username,
                "forked": forked
            })
        except:
            return render(request, "repo/file.html", {
                "decode": False,
                "url": f.url,
                "repo": repo,
                "username": username,
                "forked": forked
            })


@csrf_exempt
@login_required(login_url='/auth/login/')
def upload(request, username, repo):

    try:
        b = request.GET["b"]
    except:
        b = "master"

    user = User.objects.get(username=username)
    r = Repository.objects.get(name=repo, user_id=user.id)

    if request.method == "POST":
        url = request.POST["path"][:-1].split("/")
        path = "/"
        subdir = Directory.objects.get(repo_id=r.id, path="/", branch=b).id
        f_url = upload_s3(request)
        for i in url:
            print(i)
            if i == "":
                break
            else:
                path += f"{i}/"
                try:
                    d = Directory.objects.get(repo_id=r.id, path=path, branch=b)
                    print(colored(path + " exist", "red"))
                except Directory.DoesNotExist:
                    Directory(repo_id=r.id, subdir=subdir, name=i, path=path, branch=b).save()
                    print(colored(path + " doesn't exist.", "blue"))
                try:
                    subdir = Directory.objects.get(repo_id=r.id, path=path, branch=b).id
                    print(colored(path + " is the new subdir", "magenta"))
                except Exception as e:
                    d = Directory.objects.filter(repo_id=r.id, path=path, branch=b)
                    d[::-1][0].delete()
                    d = Directory.objects.get(repo_id=r.id, path=path, branch=b)
                    subdir = d.id

        File(repo_id=r.id, filename=request.FILES["file"].name, subdir=subdir, url=f_url, branch=b, path=path+request.FILES["file"].name+"/").save()

        try:
            c = Commit.objects.get(commit_id=request.POST["commit_id"], branch=b)
        except:
            Commit(commit_id=request.POST["commit_id"], repo_id=r.id, user_id=request.user.id, message=request.POST["message"], branch=b).save()
            c = Commit.objects.get(commit_id=request.POST["commit_id"], branch=b)

        f = File.objects.get(repo_id=r.id, filename=request.FILES["file"].name, subdir=subdir, url=f_url, branch=b, path=path+request.FILES["file"].name+"/")
        Commit_File(commit_id=c.commit_id, file=f.id).save()

        return JsonResponse({"data": "success"})

    else:
        return render(request, "repo/upload.html", {
            "repo": repo,
            "username": username,
            "commit_id": str(uuid.uuid4()),
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


def delete_repo(request, username, repo):
    user = User.objects.get(username=username)
    repo = Repository.objects.get(user_id=user.id, name=repo)
    Directory.objects.filter(repo_id=repo.id).delete()
    File.objects.filter(repo_id=repo.id).delete()
    Branch.objects.filter(repo_id=repo.id).delete()
    repo.delete()
    return HttpResponseRedirect("/")


def change_repo_visibility(request, username, repo):
    user = User.objects.get(username=username)
    repo = Repository.objects.get(user_id=user.id, name=repo)
    status = 0
    if request.POST["status"] == "private":
        status = 1
    repo.status = status
    repo.save()
    return HttpResponseRedirect(f"/repo/{username}/{repo.name}")


def fork(request, username, repo):
    user = User.objects.get(username=username)
    r = Repository.objects.get(user_id=user.id, name=repo)
    Repository(user_id=request.user.id, name=repo, description=r.description, status=r.status, fork=r.id).save()
    user_r = Repository.objects.get(user_id=request.user.id, name=repo, description=r.description, status=r.status)
    Branch(repo_id=user_r.id, name="master").save()

    dirs = Directory.objects.filter(repo_id=r.id)

    for d in dirs:
        if d.path == "/":
            Directory(repo_id=user_r.id, subdir=0, name=d.name, path=d.path, branch=d.branch).save()
        else:
            path = d.path.split("/")
            path.pop(len(path)-1)
            path.pop(len(path)-1)
            subdir_path = dirize(path)
            print(colored((d.path, d.path.split("/"), path, subdir_path), "red"))
            subdir = Directory.objects.get(repo_id=user_r.id, path=subdir_path)
            Directory(repo_id=user_r.id, subdir=subdir.id, name=d.name, path=d.path, branch=d.branch).save()

        dir = Directory.objects.get(repo_id=user_r.id, path=d.path)
        files = File.objects.filter(repo_id=r.id, subdir=d.id)

        for f in files:
            File(repo_id=user_r.id, filename=f.filename, subdir=dir.id, branch=f.branch, path=f.path, url=f.url).save()

    return HttpResponseRedirect(f"/repo/{request.user.username}/{repo}")


def change_name(request, username, repo):
    u = User.objects.get(username=username)
    r = Repository.objects.get(user_id=u.id, name=repo)
    r.name = request.POST["name"]
    r.save()
    return HttpResponseRedirect(f"/repo/{username}/{request.POST['name']}")


def star(request, username, repo):
    user = User.objects.get(username=username)
    r = Repository.objects.get(name=repo)
    Star(user_id=user.id, repo_id=r.id).save()
    return HttpResponseRedirect(f"/repo/{username}/{repo}/")