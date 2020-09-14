from django.shortcuts import render
from main.models import Repository, Directory, File
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from main.models import Repository, Directory, File, Commit
from django.contrib.auth.models import User

from termcolor import colored

import random
from string import ascii_letters, digits

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
        data["directories"][d.id] = [d.dir_id, d.name, d.path]

    for f in files:
        data["files"].append([f.id, f.filename, f.url, f.directory_id])

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