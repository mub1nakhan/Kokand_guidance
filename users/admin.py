from django.contrib import admin
from users.models import UserRole, LanguageCode, CustomUserManager, CustomUser, UserProfile


admin.site.register(UserProfile)
# admin.site.register(UserRole)
# admin.site.register(LanguageCode)
admin.site.register(CustomUser)
# admin.site.register(CustomUserManager)

