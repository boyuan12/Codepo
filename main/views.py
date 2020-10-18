from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
import os
import GitHubClone.settings as settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.admin import User
from .models import Repository, File, Directory, Profile, Follows, Branch, Issue, Tags, Issue_Comment, Commit, Commit_File, Profile
from repo.views import get_s3
from oauth.models import OAuth, Uri, Token
import cloudinary
import cloudinary.uploader
import cloudinary.api
import requests
import random
import string
from termcolor import colored
import boto3
import pathlib
from django.views.decorators.csrf import csrf_exempt


cloudinary.config(
    cloud_name = "boyuan12",
    api_key = "893778436618783",
    api_secret = "X4LufXPHxvv4hROS3VZWYyR3tIE"
)

def random_words(n=3):
    word_site = "http://svnweb.freebsd.org/csrg/share/dict/words?view=co&content-type=text/plain"
    response = requests.get(word_site)
    WORDS = response.content.splitlines()
    words = ""
    for i in range(n):
        word = random.choice(WORDS).decode("utf-8")
        words += word.capitalize()
    return words


def random_str(n):
    s = ""
    for i in range(n):
        s += random.choice(string.ascii_letters + string.digits)
    return s

def validate_date(s):
    if len(str(s)) == 1:
        return "0" + str(s)
    return str(s)

def validate_url(url):
    # https://stackoverflow.com/questions/7160737/python-how-to-validate-a-url-in-python-malformed-or-not
    import re
    regex = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return re.match(regex, url) is not None

# Create your views here.
def index(request):
    if request.user.is_authenticated:
        repos = Repository.objects.filter(user_id=request.user.id)
        return render(request, "main/index.html", {
            "repos": repos
        })
    else:
        return render(request, "main/home.html")


@login_required(login_url='/auth/login/')
def new(request):
    if request.method == "POST":

        status = None
        if request.POST["status"] == "public":
            status = 0
        else:
            status = 1

        try:
            Repository.objects.get(user_id=request.user.id, name=request.POST["name"])
            return HttpResponseRedirect(f"/repo/{request.user.username}/{request.POST['name']}")
        except:
            pass

        r = Repository(user_id=request.user.id, name=request.POST["name"], description=request.POST["description"], status=status)
        r.save()

        d = Directory(repo_id=Repository.objects.get(user_id=request.user.id, name=request.POST["name"], description=request.POST["description"], status=status).id, name="/", subdir=0, path="/", branch="master")
        d.save()

        b = Branch(repo_id=Repository.objects.get(user_id=request.user.id, name=request.POST["name"], description=request.POST["description"], status=status).id, name="master")
        b.save()

        return HttpResponseRedirect(f"/repo/{request.user.username}/{request.POST['name']}/")

    else:
        return render(request, "main/new.html")

@login_required(login_url='/auth/login/')
def profile(request, username):

    try:
        user = User.objects.get(username=username)
    except:
        return HttpResponse("user doesn't exist")

    tab = ""

    try:
        if request.GET["tab"] == "repo":
            tab = "repo"
    except:
        tab = "overview"

    repos = Repository.objects.filter(user_id=user.id)

    try:
        p = Profile.objects.get(user_id=user.id)
    except:
        p = []

    following = (Follows.objects.filter(following=user.id))
    follows = (Follows.objects.filter(user_id=user.id))
    followed = False

    for i in following:
        if i.following == user.id:
            followed = True

    return render(request, "main/user.html", {
        "username": username,
        "tab": tab,
        "repos": repos,
        "user": user,
        "p": p,
        "follows": follows,
        "following": following,
        "followed": followed
    })


@login_required(login_url='/auth/login/')
def edit_profile(request):
    if request.method == "POST":
        try:
            r = cloudinary.uploader.upload(request.FILES['file'])
            img_url = r["secure_url"]
        except:
            pass

        try:
            p = Profile.objects.get(user_id=request.user.id)
            p.description = request.POST["desc"]
            p.organization = request.POST["org"]
            p.location = request.POST["loc"]
            p.website = request.POST["web"]
            try:
                p.avatar = img_url
                request.session["img"] = img_url
            except:
                pass
            p.save()
        except:
            try:
                p = Profile(user_id=request.user.id, description=request.POST["desc"], organization=request.POST["org"], location=request.POST["loc"], website=request.POST["web"], avatar=img_url)
            except:
                p = Profile(user_id=request.user.id, description=request.POST["desc"], organization=request.POST["org"], location=request.POST["loc"], website=request.POST["web"], avatar="https://iupac.org/wp-content/uploads/2018/05/default-avatar.png")
            p.save()

        return HttpResponseRedirect("/profile/")

    else:
        try:
            p = Profile.objects.get(user_id=request.user.id)
        except:
            p = []

        try:
            oauth = OAuth.objects.filter(user_id=request.user.id)
        except:
            oauth = []

        uris = {}
        for o in oauth:
            uris[o.client_id] = Uri.objects.filter(client_id=o.client_id)

        return render(request, "main/profile.html", {
            "p": p,
            "oauth": oauth,
            "uris": uris,
        })


@login_required(login_url='/auth/login/')
def follow_user(request):
    user = User.objects.get(username=request.GET["username"])
    f = Follows(user_id=request.user.id, following=user.id)
    f.save()

    print(f)

    return JsonResponse({"message": "success"})


@login_required(login_url='/auth/login/')
def unfollow_user(request):
    user = User.objects.get(username=request.GET["username"])
    print(request.user.id, user.id)
    Follows.objects.filter(user_id=request.user.id, following=user.id).delete()
    return JsonResponse({"message": "success"})


@login_required(login_url='/auth/login/')
def create_oauth_app(request):
    # app = OAuth(user_id=request.user.id, client_id=)
    if request.method == "POST":
        client_id = random_str(20)
        try:
            while True:
                OAuth.objects.get(client_id=client_id)
                client_id = random_str(20)
        except:
            pass

        app = OAuth(user_id=request.user.id, name=request.POST["name"], client_id=client_id,    client_secret=random_str(50))
        app.save()

        if request.POST["redirect_uri"] == "N/A":
            pass
        else:
            uris = request.POST["redirect_uri"].split(",")
            for i in uris:
                if validate_url(i):
                    u = Uri(client_id=client_id, redirect_uri=i)
                    u.save()

        return HttpResponseRedirect("/profile/")


@login_required(login_url="/auth/login/")
def create_new_branch(request):
    if request.method == "POST":
        b = request.POST["name"]
        r = request.POST["repo"]

        r = Repository.objects.get(user_id=request.user.id, name=r)
        b = Branch(repo_id=r.id, name=b)
        b.save()
        d = Directory(repo_id=r.id, subdir=0, name="/", path="/", branch=request.POST["name"])
        d.save()

        return HttpResponseRedirect(f"/repo/{request.user.username}/{request.POST['repo']}/?b={request.POST['name']}")


@login_required(login_url="/auth/login/")
def repo_settings(request, username, repo):
    if request.method == "POST":
        pass
    else:
        r = Repository.objects.get(user_id=request.user.id, name=repo)
        print(r.status)
        return render(request, "main/settings.html", {
            "username": username,
            "repo": repo,
            "status": r.status
        })


@login_required(login_url="/auth/login/")
def repo_issues(request, username, repo):
    if request.method == "POST":
        pass
    else:
        user = User.objects.get(username=username)
        r = Repository.objects.get(name=repo, user_id=user.id)
        issues = Issue.objects.filter(repo_id=r.id)
        issue = []
        for i in issues:
            username = User.objects.get(id=i.user_id).username
            tags = Tags.objects.filter(issue_id=i.id)
            print(tags)
            issue.append([i.id, i.title, (i.timestamp.year, i.timestamp.month, i.timestamp.day, i.timestamp.hour, i.timestamp.minute), username, [tag.name for tag in tags], i.issue_id, i.status])

        return render(request, "main/issue.html", {
            "issues": issue
        })


@login_required(login_url="/auth/login/")
@csrf_exempt
def repo_new_issue(request, username, repo):
    if request.method == "POST":
        user = User.objects.get(username=username)
        repo = Repository.objects.get(user_id=user.id, name=repo)
        issue_id = len(Issue.objects.filter(repo_id=repo.id))
        Issue(issue_id=issue_id+1, user_id=request.user.id, repo_id=repo.id, title=request.POST["title"], content=request.POST["content"]).save()
        issue = Issue.objects.get(issue_id=issue_id+1)
        print(colored(str(request.POST)))
        for t in request.POST.getlist("tags"):
            # print(t)
            Tags(repo_id=repo.id, issue_id=issue.id, name=t).save()
        return HttpResponse("success")
    else:
        p = Profile.objects.get(user_id=User.objects.get(username=username).id)
        return render(request, "main/new-issue.html", {
            "avatar": p.avatar,
            "username": username,
            "repo": repo
        })


def view_issue(request, username, repo, issue_id):
    if request.method == "POST":
        try:
            request.POST["delete"]
            user = User.objects.get(username=username)
            r = Repository.objects.get(user_id=user.id, name=repo)
            i = Issue.objects.get(repo_id=r.id, user_id=user.id, issue_id=issue_id)
            i.status = 1
            i.save()
            Issue_Comment(repo_id=r.id, issue_id=issue_id, user_id=request.user.id, message="Issue Closed", special=0).save()
            return HttpResponseRedirect(f"/{username}/{repo}/issues/{issue_id}")
        except Exception as e:
            try:
                request.POST["reopen"]
                user = User.objects.get(username=username)
                r = Repository.objects.get(user_id=user.id, name=repo)
                i = Issue.objects.get(repo_id=r.id, user_id=user.id, issue_id=issue_id)
                i.status = 0
                i.save()
                Issue_Comment(repo_id=r.id, issue_id=issue_id, user_id=request.user.id, message="Issue Reopened", special=1).save()
            except Exception as e:
                print(colored(str(e), "red"))
                user = User.objects.get(username=username)
                r = Repository.objects.get(user_id=user.id, name=repo)
                comment = request.POST["comment"]
                Issue_Comment(repo_id=r.id, issue_id=issue_id, user_id=request.user.id, message=comment).save()
                return HttpResponseRedirect(f"/{username}/{repo}/issues/{issue_id}")
    else:
        user = User.objects.get(username=username)
        repo = Repository.objects.get(name=repo, user_id=user.id)
        issue = Issue.objects.get(issue_id=issue_id, repo_id=repo.id)
        tags = Tags.objects.filter(issue_id=issue.id)
        comments = Issue_Comment.objects.filter(repo_id=repo.id, issue_id=issue_id)
        cs = []
        for c in comments:
            avatar = Profile.objects.get(user_id=c.user_id).avatar
            username = User.objects.get(id=c.user_id).username
            cs.append([avatar, c.repo_id, c.issue_id, c.message, (c.timestamp.year, c.timestamp.month, c.timestamp.day, c.timestamp.hour, c.timestamp.minute), c.id, username, c.special])

        able_close_issue = "False"
        if request.user.id == repo.user_id or request.user.id == issue.user_id:
            able_close_issue = "True"

        print(colored(cs, "red"))
        # print(cs[len(cs)-1][7] == 0)

        if len(cs) == 0:
            return render(request, "main/view-issue.html", {
                "issue": issue,
                "tags": tags,
                "author_avatar": Profile.objects.get(user_id=user.id).avatar,
                "comments": cs,
                "able_close_issue": able_close_issue,
                "issue_closed": 0
            })
        else:
            return render(request, "main/view-issue.html", {
                "issue": issue,
                "tags": tags,
                "author_avatar": Profile.objects.get(user_id=user.id).avatar,
                "comments": cs,
                "able_close_issue": able_close_issue,
                "issue_closed": cs[len(cs)-1][7] == 0
            })


def view_all_commits(request, username, repo):

    try:
        b = request.GET["b"]
    except:
        b = "master"

    user = User.objects.get(username=username)
    r = Repository.objects.get(user_id=user.id, name=repo)
    commits = Commit.objects.filter(repo_id=r.id, branch=b)[::-1]
    data = []
    for c in commits:
        u = User.objects.get(id=c.user_id)
        p = Profile.objects.get(user_id=u.id)
        data.append([c.commit_id, u.username, p.avatar, c.message, validate_date(c.timestamp.year), validate_date(c.timestamp.month), validate_date(c.timestamp.day), c.timestamp])
    return render(request, "main/commits.html", {
        "data": data
    })


def view_single_commit(request, username, repo, commit_id):
    user = User.objects.get(username=username)
    r = Repository.objects.get(user_id=user.id, name=repo)
    files = Commit_File.objects.filter(commit_id=commit_id)
    data = []
    for f in files:
        try:
            file = File.objects.get(pk=f.file)
            try:
                data.append([file.path, get_s3(file.url).decode("utf-8")])
            except:
                data.append([file.path, file.url, "undecodeable"])
        except:
            if f.code == 0:
                status = "deleted"
            data.append([f.path, status])
    return render(request, "main/commit.html", {
        "data": data
    })