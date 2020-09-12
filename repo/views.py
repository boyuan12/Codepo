from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect, Http404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.core.files.storage import FileSystemStorage

import os

from main.models import Repository, Directory, File, Branch, Star
import requests

from GitHubClone.settings import DEBUG

import boto3
import random
import string
import pathlib

from termcolor import colored

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

# Create your views here.
# @login_required(login_url='/auth/login/')
def repo(request, username, repo, path="/"):

    try:
        b = request.GET["b"]
    except:
        b = "master"

    user = User.objects.get(username=username)
    r = Repository.objects.get(name=repo, user_id=user.id)

    if "/" not in path or path != "/":
        path = "/" + path + "/"

    # check for directory or file using path
    try:
        d = Directory.objects.get(repo_id=r.id, path=path, branch=b)
        dirs = Directory.objects.filter(repo_id=r.id, subdir=d.id, branch=b)
        print(dirs)
        files = File.objects.filter(repo_id=r.id, subdir=d.id, branch=b)
        return render(request, "repo/repo.html", {
            "files": files,
            "dirs": dirs
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
                "content": content.decode("utf-8")
            })
        except:
            return render(request, "repo/file.html", {
                "decode": False,
                "url": f.url
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
        subdir = Directory.objects.get(repo_id=r.id, path="/").id
        f_url = upload_s3(request)
        for i in url:
            print(i)
            if i == "":
                break
            else:
                path += f"{i}/"
                try:
                    d = Directory.objects.get(repo_id=r.id, path=path)
                    print(colored(path + " exist", "red"))
                except Directory.DoesNotExist:
                    Directory(repo_id=r.id, subdir=subdir, name=i, path=path, branch=b).save()
                    print(colored(path + " doesn't exist.", "blue"))
                try:
                    subdir = Directory.objects.get(repo_id=r.id, path=path).id
                    print(colored(path + " is the new subdir", "magenta"))
                except Exception as e:
                    d = Directory.objects.filter(repo_id=r.id, path=path)
                    d[::-1][0].delete()
                    d = Directory.objects.get(repo_id=r.id, path=path)
                    subdir = d.id

        File(repo_id=r.id, filename=request.FILES["file"].name, subdir=subdir, url=f_url, branch=b, path=path+request.FILES["file"].name+"/").save()

        return JsonResponse({"data": "success"})

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
    # user = User.objects.get(username=username)
    # r_org = Repository.objects.get(user_id=user.id, name=repo)
    # dirs = Directory.objects.filter(repo_id=r_org.id)
    # r = Repository(user_id=request.user.id, name=repo, description=r_org.description, status=r_org.status)
    # r.save()
    # dir_ids = {}
    # r = Repository.objects.get(user_id=request.user.id, name=repo)
    # for d in dirs:
    #     # a = Directory(repo_id=r.id, dir_id=d.id, name=d.name, path=d.path, branch=)
    #     try:
    #         Directory(repo_id=r.id, dir_id=dir_ids[r.dir_id], name=d.name, path=d.path, branch=d.branch).save()
    #     except KeyError:
    #         Directory(repo_id=r_org.id, dir_id=)
    #         pass
    #     pass
    # return HttpResponse(str(Directory.objects.filter(id=r.id)))
    pass


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