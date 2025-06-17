from django.contrib import admin
from .models import Garden, Plant, Note, AIRecommendation, PlantType

# # Register your models here.
# admin.site.register(Garden)
# admin.site.register(Plant)
# admin.site.register(Note)
# admin.site.register(AIRecommendation)
# admin.site.register(PlantType)

@admin.register(Garden)
class GardenAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description', 'owner', 'image')  # Display key fields
    search_fields = ('name', 'description', 'owner__username')  # Enable search by name, description, and owner
    list_filter = ('owner',)  # Filter by owner
    filter_horizontal = ('users_with_access',)  # Add horizontal filter for ManyToManyField

@admin.register(PlantType)
class PlantTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')  # Display key fields
    search_fields = ('name',)  # Enable search by name

@admin.register(Plant)
class PlantAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'plant_type', 'garden', 'planted_date', 'image')  # Display key fields
    search_fields = ('name', 'plant_type__name', 'garden__name')  # Enable search by name, plant type, and garden
    list_filter = ('plant_type', 'garden', 'planted_date')  # Filter by plant type, garden, and planted date

@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_plants', 'date', 'content', 'image')  # Display key fields
    search_fields = ('content', 'plant__name')  # Enable search by content and plant name
    list_filter = ('date',)  # Filter by date

    def get_plants(self, obj):
        return ", ".join([plant.name for plant in obj.plant.all()])
    get_plants.short_description = 'Plants'

@admin.register(AIRecommendation)
class AIRecommendationAdmin(admin.ModelAdmin):
    list_display = ('id', 'plant', 'recommendation', 'created_at')  # Display key fields
    search_fields = ('recommendation', 'plant__name')  # Enable search by recommendation and plant name
    list_filter = ('created_at',)  # Filter by creation date