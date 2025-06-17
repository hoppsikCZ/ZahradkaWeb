from django.urls import path

from gardening import views

urlpatterns = [
    path('', views.index, name='index'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('gardens/', views.gardens_view, name='gardens'),
    path('gardens/add/', views.garden_add_view, name='garden_add'),
    path('gardens/<int:garden_id>/', views.garden_detail_view, name='garden_detail'),
    path('gardens/<int:garden_id>/edit/', views.garden_edit_view, name='garden_edit'),
    path('gardens/<int:garden_id>/delete/', views.garden_delete_view, name='garden_delete'),

    path('gardens/<int:garden_id>/plants/add/', views.plant_add_view, name='plant_add'),
    path('gardens/<int:garden_id>/plants/<int:plant_id>/edit/', views.plant_edit_view, name='plant_edit'),
    path('gardens/<int:garden_id>/plants/<int:plant_id>/delete/', views.plant_delete_view, name='plant_delete'),
    path('plant-types/', views.plant_type_list_view, name='plant_type_list'),
    path('plant-types/add/', views.plant_type_add_view, name='plant_type_add'),
    path('plant-types/<int:type_id>/delete/', views.plant_type_delete_view, name='plant_type_delete'),
    path('plants/<int:plant_id>/recommendations/', views.plant_recommendations_view, name='plant_recommendations'),
]

