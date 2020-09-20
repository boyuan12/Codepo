import requests
import os
import boto3
import random
import string
import pathlib
import uuid
import json
import os

S3_ACCESS_KEY_ID = requests.get("https://pastebin.com/raw/BZL992sw").text.split("\r\n")[0]
S3_SECRET_ACCESS_KEY = requests.get("https://pastebin.com/raw/BZL992sw").text.split("\r\n")[1]

s3 = boto3.resource("s3", aws_access_key_id=S3_ACCESS_KEY_ID, aws_secret_access_key=S3_SECRET_ACCESS_KEY)

def random_str(n):
    s = ""
    for i in range(n):
        s += random.choice(string.ascii_letters + string.digits)
    return s

def get_s3(name):
    obj = s3.Object("githubclone", f"{name}")
    body = obj.get()['Body'].read()
    return body

def upload_s3(content, filename):
    name = random_str(10)
    s3.Bucket('githubclone').put_object(Key=f"{name}{pathlib.Path(filename).suffix}", Body=content, ACL="public-read")
    return f"{name}{pathlib.Path(filename).suffix}"


def clone(username, repo):
    # username = input("Username: ")
    # repo = input("Repository: ")

    r = requests.get(f"https://github-clone-dj.herokuapp.com/api/repo/?username={username}&repo={repo}").json()
    for key, val in r["directories"].items():
        try:
            os.mkdir(val[1][1:len(val[1])-1])
        except:
            pass

    for i in r["files"]:
        with open(i[3][1:len(i[3])-1], "wb") as f:
            f.write(get_s3(i[2]))

    try:
        os.mkdir(".gitt")
    except:
        pass

    with open(".gitt/info.txt", "w") as f:
        f.write(username + "\n" + repo)
        f.close()


def commit(message, branch):

    updates = {"new": [], "changed": [], "delete": []}

    with open(".gitt/info.txt") as f:
        username, repo = f.read().split("\n")
        f.close()

    fs = [] # local repo's files (compare for deleted files)
    org = [] # original files from remote repo (compare for deleted files)

    r = requests.get(f"https://github-clone-dj.herokuapp.com/api/repo/?username={username}&repo={repo}").json()["files"]
    for _ in r:
        org.append(_[3])

    for dir_, _, files in os.walk(os.getcwd()):
        for file_name in files:
            rel_dir = os.path.relpath(dir_, os.getcwd())
            if rel_dir == ".":
                path = os.path.join(rel_dir, file_name)[1:len(os.path.join(rel_dir, file_name))] + "/"
            else:
                if rel_dir == ".gitt":
                    continue
                path = "/" + os.path.join(rel_dir, file_name) + "/"

            fs.append(path)

            r = requests.get(f"https://github-clone-dj.herokuapp.com/api/file-data/?username={username}&repo={repo}&path={path}").json()
            print(r)
            try:
                r["error"]
                with open(path[1:len(path)-1], "rb") as f:
                    a = f.read()
                    updates["new"].append([upload_s3(a, path), path])
                    f.close()
            except:
                with open(path[1:len(path)-1], "rb") as f:
                    a = f.read()
                    b = get_s3(r["url"])
                    if a != b:
                        updates["changed"].append([upload_s3(a, path), path])
                    f.close()

    for _ in org:
        if _ not in fs:
            updates["delete"].append(_)

    # print(fs, org)
    print(updates)

    commit_id = uuid.uuid4()

    requests.post("https://github-clone-dj.herokuapp.com/api/commit/", data={
        "username": username,
        "repo": repo,
        "data": json.dumps(updates),
        "id": commit_id,
        "message": message,
        "branch": branch
    })



def main():
    import argparse
    parser = argparse.ArgumentParser(description = "CLI for GitHub Clone")
    parser.add_argument("-clone", type=str, nargs=2, default=None, metavar=("username", "repo"),
                        help = "Clone a repository")
    parser.add_argument("-commit", nargs=2, default=None, metavar=("commit message", "branch"),
                        help="")
    args = parser.parse_args()

    if args.clone is not None:
        clone(args.clone[0], args.clone[1])
    elif args.commit is not None:
        commit(args.commit[0], args.commit[1])

if __name__ == "__main__":
    main()
