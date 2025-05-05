from django.contrib import admin
from .models import Garden, Plant, Note, AIRecommendation, PlantType

# Register your models here.
admin.site.register(Garden)
admin.site.register(Plant)
admin.site.register(Note)
admin.site.register(AIRecommendation)
admin.site.register(PlantType)