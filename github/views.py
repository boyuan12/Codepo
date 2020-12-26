from django.shortcuts import render
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import base
import requests
from requests.api import get
from termcolor import colored
from helpers import base64_decode, base64_encode
from main.models import Repository, File, Directory
import json
from django.contrib.auth.models import User
from repo.views import get_s3, upload_s3
import os


# Create your views here.
GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")

def files_in_folder(gh_access_token, path, username, repo, repo_id, request=None):
    r = requests.get(f"https://api.github.com/repos/{username}/{repo}/contents/" + path, headers={
        "Authorization": f"token {gh_access_token}"
    })
    for i in r.json():
        print(colored(path + "/", "red"))
        subdir = Directory.objects.get(repo_id=repo_id, path=path + "/")
        if i["type"] == "dir":
            Directory(repo_id=repo_id, subdir=subdir.id, name=i["name"], path=path + "/" + i["name"] + "/", branch="master").save()
            files_in_folder(gh_access_token, path + "/" + i["name"], username, repo, repo_id)
        else:
            content = requests.get(i["download_url"]).text
            File(repo_id=repo_id, filename=i["name"], subdir=subdir.id, url=upload_s3(request, data=content, filename=i["name"]), branch="master", path=path + "/" + i["name"] + "/").save()
            print(path + "/" + i["name"])


def github_auth(request):
    if request.GET.get("next"):
        return HttpResponseRedirect(f"https://github.com/login/oauth/authorize?client_id={GITHUB_CLIENT_ID}&state={base64_encode(request.GET.get('next'))}&scope=repo")
    return HttpResponseRedirect(f"https://github.com/login/oauth/authorize?client_id={GITHUB_CLIENT_ID}")


def github_callback(request):
    r = requests.post("https://github.com/login/oauth/access_token", data={
        "client_id": GITHUB_CLIENT_ID,
        "client_secret": GITHUB_CLIENT_SECRET,
        "code": request.GET["code"]
    }, headers={
        "Accept": "application/json"
    })

    request.session["github_access_token"] = r.json()["access_token"]

    if request.GET.get("state"):
        return HttpResponseRedirect(base64_decode(request.GET.get("state")))
    return HttpResponseRedirect("/")


def create_repo(request, username, repo):
    if request.method == "POST":
        
        r = requests.post("https://api.github.com/user/repos", data=json.dumps({
            "name": request.POST["name"],
        }), headers={
            "Authorization": f"token {request.session['github_access_token']}",
            "Accept": "application/vnd.github.v3+json",
        })


        r = requests.get("https://api.github.com/user", headers={
            "Authorization": f"token {request.session['github_access_token']}"
        })
        gh_username = r.json()["login"]

        user = User.objects.get(username=username)
        r = Repository.objects.get(user_id=user.id, name=repo)

        files = File.objects.filter(repo_id=r.id)

        for f in files:
            try:
                r = requests.put(f"https://api.github.com/repos/{gh_username}/{request.POST['name']}/contents{f.path[:-1]}", data=json.dumps({
                    "message": "Commit Automatically from CodeHub",
                    "content": base64_encode(get_s3(f.url).decode("utf-8")),
                }), headers={
                    "Authorization": f"token {request.session['github_access_token']}"
                })
                print(f.filename, f.path, r.json())
            except Exception as e:
                print(e)
                pass

        
        return HttpResponseRedirect(f"https://github.com/{gh_username}/{request.POST['name']}")

    else:
        r = requests.get("https://api.github.com/user", headers={
            "Authorization": f"token {request.session['github_access_token']}"
        })
        avatar_url = r.json()["avatar_url"]
        gh_username = r.json()["login"]
        return render(request, "github/create-repo.html", {
            "repo": repo,
            "avatar_url": avatar_url,
            "gh_username": gh_username
        })


def sync_repo(request):
    if request.method == "POST":
        Repository(user_id=request.user.id, name=request.POST["repo"], description="", status=0).save()
        repo_id = Repository.objects.get(user_id=request.user.id, name=request.POST["repo"]).id
        Directory(repo_id=repo_id, subdir=0, name="", path="/" , branch="master").save()
        
        print(repo_id)
        files_in_folder(request.session["github_access_token"], "", request.POST["username"], request.POST["repo"], repo_id)

        return HttpResponseRedirect(f"/repo/{request.user.username}/{request.POST['repo']}")

    else:
        # r = requests.get("https://api.github.com/user/repos", headers={
        #     "Authorization": f"token {request.session['github_access_token']}",
        #     # "Accept": "application/vnd.github.v3+json",
        # })
        # return JsonResponse(r.json(), safe=False)

        return render(request, "github/sync-repo.html")
