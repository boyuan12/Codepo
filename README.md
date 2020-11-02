# GitHub Clone
## Introduction
This is my try to develop a web application similar to [GitHub](https://github.com), which is where you suppose to find and read this document. I tried my best to implement different essential functionalities that GitHub Provides (See features below for details) as a clone, entire web application is written in Python/Django. I will constantly add more feature to it. Of course there's going to be a lot of bugs, please feel free to open an issue by using issue template, or you can request more feature using feature request template.

Website: [https://github-clone-dj.herokuapp.com](https://github-clone-dj.herokuapp.com)

## Motivation
The motivation behind this project is to create a custom code-storing system. I really interested on how GitHub works underneath the hood, so I created a Django web application.

## Features
### Authentication
To use most of the feature that this website provides, the user need to create an account at /auth/register/ *(protected by reCAPTCHA)*, or login at /auth/login/. Currently it doesn't support OAuth.
![](https://res.cloudinary.com/boyuan12/image/upload/v1600326627/Screen_Shot_2020-09-17_at_12.10.21_AM_kbmfmq.png) 

![](https://res.cloudinary.com/boyuan12/image/upload/v1600326713/Screen_Shot_2020-09-17_at_12.11.47_AM_jkqeoi.png)

### Repository
Once logged in an account, the user will be able to create a new repository at /new/, which going to ask the user for name, description, private/public.
![](https://res.cloudinary.com/boyuan12/image/upload/v1600326795/Screen_Shot_2020-09-17_at_12.13.08_AM_mkoybu.png)

### Branches
User can also create different branches for their repository, by default, a branch named "master" will be created and selected by default. To create a new branch, just click on the Branches dropdown, and enter a new branch name. To access different branch, whether on Add Files or Commits, just add `?b=BRANCH_NAME` at the end of the URL.
![](https://res.cloudinary.com/boyuan12/image/upload/t_media_lib_thumb/v1600326986/Screen_Shot_2020-09-17_at_12.16.18_AM_jvvpub.png)

### Add Files
Once a new repository have been created, user can upload file through the root directory via /repo/<username>/<repository_name>/upload/, user can just drag and drop file with a commit message, and it will upload automatically with the commit message provided. If branch is provided, it's going to upload to the given branch, and the commit will be commited to the given branch as well. 
![](https://res.cloudinary.com/boyuan12/image/upload/v1600365405/Screen_Shot_2020-09-17_at_10.56.37_AM_v5zlvm.png)
(P.S. Yes, I use Grammarly)

### Commits
Speaking of commits, the user will be able to view a commit for each change the made at `/repo/<username>/<repository_name>/commits/`, which going to show all commits within a specific branch, if sepecified. Default branch is master.
![](https://res.cloudinary.com/boyuan12/image/upload/v1600370180/Screen_Shot_2020-09-17_at_12.15.38_PM_txpp7n.png)

You could also view file that commited by a specific branch (currently only support view file that are added) at `/repo/<username>/<repository_name>/commit/<commit_id>`.
![](https://res.cloudinary.com/boyuan12/image/upload/v1600370337/Screen_Shot_2020-09-17_at_12.18.51_PM_ccut13.png)

### Issues
You could also view all issues at `/repo/<username>/<repository_name>/issues/`.
![](https://res.cloudinary.com/boyuan12/image/upload/v1600370842/Screen_Shot_2020-09-17_at_12.27.14_PM_ey8s9l.png)

If you need to create a new issue, just click on "New Issue" button as shown above, or go to `/repo/<username>/<repository_name>/issues/new/`. Just like GitHub, the description is Markdown friendly, and you can click on "Preview" to view what's the description looks like
![](https://res.cloudinary.com/boyuan12/image/upload/v1600373643/Screen_Shot_2020-09-17_at_1.13.56_PM_ti6ksq.png)

You can also comment an issue on expressing your own opinion, just click on a link on view all issues.
![](https://res.cloudinary.com/boyuan12/image/upload/v1600374373/Screen_Shot_2020-09-17_at_1.26.06_PM_hewhc1.png)

If you are the repository owner, or issue owner, you will see "Close Issue" button. Once you click on it, the issue will close and no further comment can be made.
![](https://res.cloudinary.com/boyuan12/image/upload/v1600374742/Screen_Shot_2020-09-17_at_1.32.15_PM_w1yajq.png)

### Pages
There's also a similar feature to GitHub Pages. For example, you created a repo and uploaded some HTML/CSS/JS files, also shown below (code available at https://github-clone-dj.herokuapp.com/repo/boyuan12345/APOD/, https://github.com/boyuan12/APOD)
![](https://res.cloudinary.com/boyuan12/image/upload/v1600375009/Screen_Shot_2020-09-17_at_1.36.43_PM_dgnqfw.png)

And it's respective Pages is available at this URL: https://github-clone-dj.herokuapp.com/p/boyuan12345/APOD/. And the page shown looks like below.
![](https://res.cloudinary.com/boyuan12/image/upload/v1600375245/Screen_Shot_2020-09-17_at_1.40.38_PM_qyznvn.png)

In general, to view Pages, the URL is `/p/<username>/<repository_name>/<path>/`.

### Profile
You could also manage your public profile that is publicly available to everybody. To see your own Public profile, go to `/<username>/`
![](https://res.cloudinary.com/boyuan12/image/upload/v1600391747/Screen_Shot_2020-09-17_at_6.14.31_PM_upt5b4.png)

To edit your profile, you can click on Edit Profile. And you will be redirect to an ugly interface, where you could add some of your personal information, change your Profile picture, etc.
![](https://res.cloudinary.com/boyuan12/image/upload/v1600392918/Screen_Shot_2020-09-17_at_6.35.12_PM_smdjnu.png)
(P.S. Have I mentioned that I use Grammarly?)

### OAuth **(BETA)**
TODO (Work in Progress, will get updated soon)

### CLI **(BETA)**
A command line interface for managing repo, work in progress

### 2-Factor Authentication
This site offer 2-Factor Authentication (2FA) for security using SMS message. To verify your phone number for 2FA, go to `/auth/2fa/`, then you should see where you can select country code, and type phone number there.
![](https://res.cloudinary.com/boyuan12/image/upload/v1604297848/Screen_Shot_2020-11-01_at_10.17.23_PM_axw7ae.png)

Then you should see "success" display on your screen. You should receive a message within 15 seconds or so (within US). The phone number it sents from +1 (916) 280-0623. You should receive a message like following:
![](https://res.cloudinary.com/boyuan12/image/upload/v1604298416/Screen_Shot_2020-11-01_at_10.26.50_PM_aulz7b.png)

Once you receive the message above, you can go to `/auth/2fa/verify/`, which you can type your code there and complete 2FA.
![](https://res.cloudinary.com/boyuan12/image/upload/v1604298531/Screen_Shot_2020-11-01_at_10.28.47_PM_a9bcub.png)

To check whether you verified your phone number, you can go to your settings (`/profile/`), and scroll down, you should see "Two-Factor Authentication". If authenticated correctly, you should see 
"Verified: Your phone number is ..."

Note that if you didn't receive your message, you can retry within 3 minutes:
![](https://res.cloudinary.com/boyuan12/image/upload/v1604298906/Screen_Recording_2020-11-01_at_10.29.57_PM_fw1ais.gif)