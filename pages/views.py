from django.shortcuts import render
from django.contrib.auth.models import User
from main.models import Repository, Directory, File
from django.http import HttpResponse
import boto3
import os
import pathlib
from termcolor import colored

# Create your views here.
s3 = boto3.resource("s3", aws_access_key_id=os.getenv("S3_ACCESS_KEY_ID"), aws_secret_access_key=os.getenv("S3_SECRET_ACCESS_KEY_ID"))

def get_s3(name):
    obj = s3.Object("githubclone", f"{name}")
    print(obj.get())
    body = obj.get()['Body'].read()
    return body


def get_s3_file_contenttype(name):
    obj = s3.Object("githubclone", name)
    return obj.get()["ResponseMetadata"]["HTTPHeaders"]["content-type"]


def index(request, username, repo, path="/"):
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
        f = File.objects.get(repo_id=r.id, subdir=d.id, branch=b, filename="index.html")
        content = get_s3(f.url)
        return HttpResponse(content.decode("utf-8"))
    except Exception as e:
        print(e)
        try:
            if path[len(path)-5:len(path)] == "html/":
                f = File.objects.get(repo_id=r.id, path=path, branch=b)
                content = get_s3(f.url)
                return HttpResponse(content.decode("utf-8"))
        except Exception as e:
            print(e)
            return HttpResponse("Not Found")
        html = path[path.find("/"):path.find(".html/")].split("/")
        html = html[len(html)-1] + ".html"
        f = File.objects.get(repo_id=r.id, path=path.replace(f"/{html}", ""), branch=b)
        content = get_s3(f.url)
        response = HttpResponse(content) # .decode("utf-8")
        if pathlib.Path(f.filename).suffix.split('.')[1] == "js":
            response["Content-Type"] = f"text/javascript"
        else:
            content_type = get_s3_file_contenttype(f.url)
            response["Content-Type"] = f"text/{pathlib.Path(f.filename).suffix.split('.')[1]}" # pathlib
        return response
