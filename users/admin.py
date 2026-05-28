from django.contrib import admin
from users.models import UserRole, LanguageCode, CustomUserManager, CustomUser, UserProfile
from django.contrib import admin

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
	list_display = ["user", "phone", "language", "total_reviews", "total_favorites"]
	search_fields = ["user__email", "phone"]

@admin.register(CustomUser)
class UserAdmin(admin.ModelAdmin):
	list_display = ["email", "full_name", "role", "is_verified", "is_active"]
	list_filter = ["role", "is_verified", "is_active"]
	search_fields = ["email", "full_name"]
	readonly_fields = ["id", "date_joined"]

