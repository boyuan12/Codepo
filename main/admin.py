from django.contrib import admin
from .models import Repository, Directory, File, Issue, Tags

# Register your models here.
admin.site.register(Repository)
admin.site.register(Directory)
admin.site.register(File)
admin.site.register(Issue)
admin.site.register(Tags)