from django.contrib import admin
from .models import Repository, Directory, File

# Register your models here.
admin.site.register(Repository)
admin.site.register(Directory)
admin.site.register(File)