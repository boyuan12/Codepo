# Repository


## Create a Repository
Once logged in an account, the user will be able to create a new repository at /new/, which going to ask the user for name, description, private/public.
![](https://res.cloudinary.com/boyuan12/image/upload/v1600326795/Screen_Shot_2020-09-17_at_12.13.08_AM_mkoybu.png)


## Upload Files
Once a new repository have been created, user can upload file through the root directory via /repo/username/repository_name/upload/, user can just drag and drop file with a commit message, and it will upload automatically with the commit message provided. If branch is provided, it's going to upload to the given branch, and the commit will be commited to the given branch as well. 
![](https://res.cloudinary.com/boyuan12/image/upload/v1600365405/Screen_Shot_2020-09-17_at_10.56.37_AM_v5zlvm.png)
(P.S. Yes, I use Grammarly)

## Commits
Speaking of commits, the user will be able to view a commit for each change the made at `/repo/<username>/<repository_name>/commits/`, which going to show all commits within a specific branch, if sepecified. Default branch is master.
![](https://res.cloudinary.com/boyuan12/image/upload/v1600370180/Screen_Shot_2020-09-17_at_12.15.38_PM_txpp7n.png)

You could also view file that commited by a specific branch (currently only support view file that are added) at `/repo/<username>/<repository_name>/commit/<commit_id>`.
![](https://res.cloudinary.com/boyuan12/image/upload/v1600370337/Screen_Shot_2020-09-17_at_12.18.51_PM_ccut13.png)

## Issues
You could also view all issues at `/repo/<username>/<repository_name>/issues/`.
![](https://res.cloudinary.com/boyuan12/image/upload/v1600370842/Screen_Shot_2020-09-17_at_12.27.14_PM_ey8s9l.png)

If you need to create a new issue, just click on "New Issue" button as shown above, or go to `/repo/<username>/<repository_name>/issues/new/`. Just like GitHub, the description is Markdown friendly, and you can click on "Preview" to view what's the description looks like
![](https://res.cloudinary.com/boyuan12/image/upload/v1600373643/Screen_Shot_2020-09-17_at_1.13.56_PM_ti6ksq.png)

You can also comment an issue on expressing your own opinion, just click on a link on view all issues.
![](https://res.cloudinary.com/boyuan12/image/upload/v1600374373/Screen_Shot_2020-09-17_at_1.26.06_PM_hewhc1.png)

If you are the repository owner, or issue owner, you will see "Close Issue" button. Once you click on it, the issue will close and no further comment can be made.
![](https://res.cloudinary.com/boyuan12/image/upload/v1600374742/Screen_Shot_2020-09-17_at_1.32.15_PM_w1yajq.png)