# Gitt
Currently, the authentication system is not supported, which means everybody can commit into a repository. The authentication system (personal token, OAuth, etc) is currently Work In Progress.

This is "gitt", a command line interface. Just like actual Git CLI, this support basic cloning and commiting.

## Installation
This is a Python CLI, so it's available at PYPI. You need to make sure you have Python 3.6 or above installed on your computer. Then type:

```
pip install gitt
```

## Features
### Cloning
After you `cd` into an empty directory, in your terminal, run:
```bash
gitt -clone USERNAME REPOSITORY_NAME
```
And you should see new files/directories created for you.

![](https://res.cloudinary.com/boyuan12/image/upload/v1601613961/Screen_Recording_2020-10-01_at_9.44.41_PM_pgfdxk.gif)

### Commiting
You can also commit using gitt. After you edit your files, in your terminal, run:
```bash
gitt -commit "COMMIT_MESSAGE" BRANCH
```