from django.shortcuts import render
from main.models import Repository, Directory, File
from django.http import HttpResponse, JsonResponse

from django.contrib.auth.models import User

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