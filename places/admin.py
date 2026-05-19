from django.contrib import admin
from places.models import Place, PlaceImage, PlaceTag

admin.site.register(Place)
admin.site.register(PlaceImage)
admin.site.register(PlaceTag)
