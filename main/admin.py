from django.contrib import admin
from .models import Repository, Directory, File, Issue, Tags, Commit, Commit_File

# Register your models here.
admin.site.register(Repository)
admin.site.register(Directory)
admin.site.register(File)
admin.site.register(Issue)
admin.site.register(Tags)
admin.site.register(Commit)
admin.site.register(Commit_File)