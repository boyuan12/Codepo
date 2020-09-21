
from django.shortcuts import render
from main.models import Repository, Directory, File
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from main.models import Repository, Directory, File, Commit, Commit_File
from django.contrib.auth.models import User

from termcolor import colored

import random
from string import ascii_letters, digits
import json
import os
import pathlib

def upload(r, b, url):
    """
        r: Repository object
        b: Branch name
        url: pure folder path for the file
        return subdir id
    """
    path = "/"
    subdir = Directory.objects.get(repo_id=r.id, path="/", branch=b).id
    url = url.split("/")
    for i in url:
        if i == "":
            break
        else:
            path += f"{i}/"
            try:
                d = Directory.objects.get(repo_id=r.id, path=path, branch=bool)
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
    return subdir

def random_str(n=150):
    string = ""
    for i in range(n):
        string += random.choice(ascii_letters + digits)
    return string


# Create your views here.
def get_structure(request):
    username = request.GET["username"]
    repo = request.GET["repo"]
    print(repo)
    user = User.objects.get(username=username)

    r = Repository.objects.get(user_id=user.id, name=repo)
    dirs = Directory.objects.filter(repo_id=r.id)
    files = File.objects.filter(repo_id=r.id)

    data = {"directories": {}, "files": []}

    for d in dirs:
        data["directories"][d.id] = [d.name, d.path]

    for f in files:
        data["files"].append([f.id, f.filename, f.url, f.path])

    return JsonResponse(data=data, safe=False)


@csrf_exempt
def create_directory(request):
    if request.method == "POST":

        username = request.POST["username"]
        user = User.objects.get(username=username)

        repo = request.POST["repo"]
        repo = Repository.objects.get(name=repo)

        directory = request.POST["directory"] # /hellollo/welcomeworld/

        dir = "/"
        subdir = "/"
        name = ""
        if directory.count("/") > 2:
            s = directory.split("/")
            for i in range(1, len(s)-2):
                print(i)
                dir += s[i]
            dir += "/"
            print(colored(dir, "green"))
            subdir += s[len(s)-2] + "/"
            name = s[len(s)-2]
        else:
            name = directory.replace("/", "")

        print(colored((subdir, name), "red"))
        subdir = Directory.objects.get(repo_id=repo.id, path=dir)
        d = Directory(repo_id=repo.id, dir_id=subdir.id, path=directory, name=name)
        d.save()

        return JsonResponse({"message": "success"})


@csrf_exempt
def delete_repository(request):

    if request.method == "POST":

        username = request.POST["username"]
        user = User.objects.get(username=username)

        repo = request.POST["repo"]
        repo = Repository.objects.get(name=repo, user_id=user.id)

        path = request.POST["path"]

        d = Directory.objects.get(repo_id=repo.id, path=path)
        File.objects.filter(repo_id=repo.id, directory_id=d.id).delete()
        d.delete()

        return JsonResponse({"message": "success"})


@csrf_exempt
def modify_file(request):

    if request.method == "POST":

        username = request.POST["username"]
        user = User.objects.get(username=username)

        repo = request.POST["repo"]
        repo = Repository.objects.get(name=repo, user_id=user.id)

        path = request.POST["path"]
        filename = request.POST["filename"]
        url = request.POST["url"]

        print(url)

        if path[0] == ".":
            path = path[1:len(path)]

        if path[len(path)-1] != "/":
            path += "/"

        print(path)
        d = Directory.objects.get(repo_id=repo.id, path=path)
        f = File.objects.filter(repo_id=repo.id, directory_id=d.id, filename=filename).update(url=url)

        return JsonResponse({"message": "success"})


@csrf_exempt
def add_file(request):

    if request.method == "POST":

        username = request.POST["username"]
        user = User.objects.get(username=username)

        repo = request.POST["repo"]
        repo = Repository.objects.get(name=repo, user_id=user.id)

        path = request.POST["path"]
        filename = request.POST["filename"]
        url = request.POST["url"]

        if path[len(path)-1] == "/" and path[len(path)-2] == "/":
            path = path[0:len(path)-1]

        d = Directory.objects.get(repo_id=repo.id, path=path)
        f = File(repo_id=repo.id, filename=filename, directory_id=d.id, url=url)
        f.save()

        return JsonResponse({"message": "success"})


@csrf_exempt
def delete_file(request):

    if request.method == "POST":

        username = request.POST["username"]
        user = User.objects.get(username=username)

        repo = request.POST["repo"]
        repo = Repository.objects.get(name=repo, user_id=user.id)

        path = request.POST["path"]
        filename = request.POST["filename"]

        try:
            d = Directory.objects.get(repo_id=repo.id, path=path)
            f = File.objects.get(repo_id=repo.id, filename=filename, directory_id=d.id).delete()
        except Exception as e:
            print(colored(str(e), "red"))
            pass

        return JsonResponse({"message": "success"})


def repos(request):

    if request.method == "GET":

        username = request.GET["username"]
        user = User.objects.get(username=username)
        repos = Repository.objects.filter(user_id=user.id)

        data = {"repos": []}

        for r in repos:
            repo_info = {}
            repo_info["name"] = r.name
            data["repos"].append(repo_info)
            print(data["repos"])

        return JsonResponse(data=data)

    else:
        return JsonResponse({"message": "Can't access other HTTP request than GET on this route."})

def sentry_webhook(request):
    print(request.POST)


@csrf_exempt
def gen_commit_id(request):
    if request.method == "POST":
        print(request)
        user = User.objects.get(username=request.user.username)
        r = Repository.objects.get(name=request.POST["repo"], user_id=user.id)
        Commit(repo_id=r.id, message=request.POST["message"]).save()
        commit_id = Commit.objects.all()[::-1][0].commit_id
        return JsonResponse({"commit_id": commit_id})


@csrf_exempt
def repo_already_exist(request):
    if request.method == "POST":
        try:
            r = Repository.objects.get(user_id=request.user.id, name=request.POST["name"])
            return JsonResponse({"exist": True})
        except:
            return JsonResponse({"exist": False})


def file_data(request):
    username = request.GET["username"]
    repo = request.GET["repo"]
    file_path = request.GET["path"]

    user = User.objects.get(username=username)
    r = Repository.objects.get(name=repo)
    try:
        f = File.objects.get(repo_id=r.id, path=file_path)
        return JsonResponse({"url": f.url})
    except Exception as e:
        print(e, file_path)
        return JsonResponse({"error": "unknown"})


@csrf_exempt
def commit(request):
    user = User.objects.get(username=request.POST["username"])
    r = Repository.objects.get(name=request.POST["repo"])
    Commit(commit_id=request.POST["id"], repo_id=r.id, user_id=user.id, message=request.POST["message"], branch=request.POST["branch"]).save()
    c = Commit.objects.get(commit_id=request.POST["id"], repo_id=r.id, user_id=user.id, message=request.POST["message"], branch=request.POST["branch"])
    data = json.loads(request.POST["data"])
    try:
        for i in data["new"]:
            aws_url = i[0]
            dir_path = str(pathlib.Path(i[1]).parent)[1:len(str(pathlib.Path(i[1]).parent))] + "/"
            print(dir_path)
            subdir = upload(r, request.POST["branch"], dir_path)
            print(subdir)
            filename = os.path.split(i[1][1:len(i[1])-1])[1]
            File(repo_id=r.id, filename=filename, subdir=subdir, url=i[0], branch=request.POST["branch"], path=i[1]).save()
            f = File.objects.get(repo_id=r.id, filename=filename, subdir=subdir, url=i[0], branch=request.POST["branch"], path=i[1])
            Commit_File(commit_id=c.commit_id, file=f.id).save()

    except KeyError:
        pass

    try:
        for i in data["changed"]:
            # print(i[1])
            # print(colored(os.path.split(i[1][:-1])[1], "red"))
            f = File.objects.get(repo_id=r.id, path=i[1])
            f.delete()
            File(repo_id=r.id, filename=os.path.split(i[1][:-1])[1], subdir=f.subdir, url=i[0], branch=request.POST["branch"], path=i[1]).save()
            f = File.objects.get(epo_id=r.id, filename=os.path.split(i[1][:-1])[1], subdir=f.subdir, url=i[0], branch=request.POST["branch"], path=i[1])
            Commit_File(commit_id=c.commit_id, file=f.id).save()
    except KeyError:
        pass

    try:
        for i in data["delete"]:
            try:
                f = File.objects.get(repo_id=r.id, path=i)
                print(i)
                f.delete()
                Commit_File(commit_id=c.commit_id, message=0, path=i).save()
            except:
                pass
    except KeyError:
        pass

    return HttpResponse("success")