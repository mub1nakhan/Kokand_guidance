from django.contrib import admin
from reviews.models import Review, ReviewImage


admin.site.register(ReviewImage)
admin.site.register(Review)


