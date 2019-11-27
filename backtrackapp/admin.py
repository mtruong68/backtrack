from django.contrib import admin

# Register your models here.
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .forms import UserCreationForm, UserChangeForm

# Delete after testing
# from .models import User
from .models import User, ProjectTeam, Project, Sprint, ProductBacklogItem, Task

class BacktrackUserAdmin(UserAdmin):
    add_form = UserCreationForm
    form = UserChangeForm
    model = User
    list_display = ['email', 'username',]

# Delete after testing
# admin.site.register(User, BacktrackUserAdmin)
admin.site.register(User)
admin.site.register(ProjectTeam)
admin.site.register(Project)
admin.site.register(Sprint)
admin.site.register(ProductBacklogItem)
admin.site.register(Task)
