from django.contrib import admin
from .models import Group


class GroupAdmin(admin.ModelAdmin):
    list_display = ("pk", "title", "slug", "description")
    search_fields = ("description",)
    prepopulated_fields = {"slug": ("title",)}


admin.site.register(Group, GroupAdmin)
