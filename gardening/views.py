from django.contrib.auth import login, authenticate, logout
from django.shortcuts import render, redirect, get_object_or_404
from gardening.forms import RegisterForm, GardenForm, PlantForm, PlantType, NoteForm
from gardening.models import Garden, Plant, Note, AIRecommendation
from django.contrib.auth.decorators import login_required
from django.utils import timezone

def index(request):
    return render(request, 'index.html')

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = RegisterForm()
    return render(request, 'auth/register.html', {'form': form})

def login_view(request):
    context = {}
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
        else:
            context = {'error': 'Neplatné uživatelské jméno nebo heslo.'}
    return render(request, 'auth/login.html', context=context)

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard_view(request):
    my_gardens = Garden.objects.filter(owner=request.user)
    shared_gardens = Garden.objects.filter(users_with_access=request.user).exclude(owner=request.user)
    return render(
        request,
        'auth/dashboard.html',
        {
            'my_gardens': my_gardens,
            'shared_gardens': shared_gardens,
        }
    )

@login_required
def gardens_view(request):
    gardens = Garden.objects.filter(owner=request.user) | Garden.objects.filter(users_with_access=request.user)
    gardens = gardens.distinct()
    return render(request, 'gardens/gardens.html', {'gardens': gardens})

@login_required
def garden_detail_view(request, garden_id):
    garden = get_object_or_404(Garden, id=garden_id)
    if not (garden.owner == request.user or request.user in garden.users_with_access.all()):
        return redirect('dashboard')
    plants = Plant.objects.filter(garden=garden)
    can_edit = garden.owner == request.user or request.user in garden.users_with_access.all()
    can_edit_users = garden.owner == request.user

    # Get selected plant
    selected_plant_id = request.GET.get('plant')
    selected_plant = None
    notes = []
    ai_recommendation = None
    if selected_plant_id:
        selected_plant = plants.filter(id=selected_plant_id).first()
        if selected_plant:
            notes = Note.objects.filter(plant=selected_plant).order_by('-date')
            ai_recommendation = AIRecommendation.objects.filter(plant=selected_plant).order_by('-created_at').first()
    else:
        selected_plant = plants.first()
        if selected_plant:
            notes = Note.objects.filter(plant=selected_plant).order_by('-date')
            ai_recommendation = AIRecommendation.objects.filter(plant=selected_plant).order_by('-created_at').first()

    # Handle AI recommendation generation
    if request.method == 'POST' and 'generate_ai' in request.POST and selected_plant:
        # Replace this with your real AI logic
        recommendation_text = f"AI Suggestion for {selected_plant.name}: Water regularly and check for pests. (This is a placeholder recommendation. I don't have a paid API key for AI services. And I don't think that sharing it in this repo is a good idea.)"
        ai_recommendation = AIRecommendation.objects.create(
            plant=selected_plant,
            recommendation=recommendation_text,
            created_at=timezone.now()
        )

    # Handle note form
    if request.method == 'POST' and 'add_note' in request.POST:
        note_form = NoteForm(request.POST, request.FILES)
        note_form.fields['plant'].queryset = plants
        if note_form.is_valid():
            note = note_form.save()
            return redirect(f"{request.path}?plant={selected_plant.id}")
    else:
        note_form = NoteForm()
        note_form.fields['plant'].queryset = plants

    return render(request, 'gardens/garden_detail.html', {
        'garden': garden,
        'plants': plants,
        'can_edit': can_edit,
        'can_edit_users': can_edit_users,
        'notes': notes,
        'note_form': note_form,
        'selected_plant': selected_plant,
        'ai_recommendation': ai_recommendation,
    })
    
@login_required
def garden_delete_view(request, garden_id):
    garden = get_object_or_404(Garden, id=garden_id)
    if not (garden.owner == request.user or request.user in garden.users_with_access.all()):
        return redirect('dashboard')
    # Only owner can delete
    if request.method == 'POST' and garden.owner == request.user:
        garden.delete()
        return redirect('dashboard')
    return render(request, 'gardens/garden_confirm_delete.html', {'garden': garden})

@login_required
def garden_add_view(request):
    if request.method == 'POST':
        form = GardenForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            garden = form.save(commit=False)
            garden.owner = request.user
            garden.save()
            form.save_m2m()
            return redirect('gardens')
    else:
        form = GardenForm(user=request.user)
    return render(request, 'gardens/garden_form.html', {'form': form, 'garden': None, 'can_edit_users': True})

@login_required
def garden_edit_view(request, garden_id):
    garden = get_object_or_404(Garden, id=garden_id)
    can_edit_users = garden.owner == request.user
    if request.method == 'POST':
        form = GardenForm(request.POST, request.FILES, instance=garden, user=request.user)
        if not can_edit_users:
            form.fields.pop('users_with_access')
        if form.is_valid():
            form.save()
            return redirect('gardens')
    else:
        form = GardenForm(instance=garden, user=request.user)
        if not can_edit_users:
            form.fields['users_with_access'].disabled = True
    return render(request, 'gardens/garden_form.html', {'form': form, 'garden': garden, 'can_edit_users': can_edit_users})

@login_required
def plant_add_view(request, garden_id):
    garden = get_object_or_404(Garden, id=garden_id)
    if not (garden.owner == request.user or request.user in garden.users_with_access.all()):
        return redirect('dashboard')
    if request.method == 'POST':
        form = PlantForm(request.POST, request.FILES)
        if form.is_valid():
            plant = form.save(commit=False)
            plant.garden = garden
            plant.save()
            return redirect('garden_detail', garden_id=garden.id)
    else:
        form = PlantForm()
    return render(request, 'plants/plant_form.html', {'form': form, 'garden': garden, 'plant': None})

@login_required
def plant_edit_view(request, garden_id, plant_id):
    garden = get_object_or_404(Garden, id=garden_id)
    if not (garden.owner == request.user or request.user in garden.users_with_access.all()):
        return redirect('dashboard')
    plant = get_object_or_404(Plant, id=plant_id, garden=garden)
    if request.method == 'POST':
        form = PlantForm(request.POST, request.FILES, instance=plant)
        if form.is_valid():
            form.save()
            return redirect('garden_detail', garden_id=garden.id)
    else:
        form = PlantForm(instance=plant)
    return render(request, 'plants/plant_form.html', {'form': form, 'garden': garden, 'plant': plant})

@login_required
def plant_delete_view(request, garden_id, plant_id):
    garden = get_object_or_404(Garden, id=garden_id)
    if not (garden.owner == request.user or request.user in garden.users_with_access.all()):
        return redirect('dashboard')
    plant = get_object_or_404(Plant, id=plant_id, garden=garden)
    if request.method == 'POST':
        plant.delete()
        return redirect('garden_detail', garden_id=garden.id)
    return render(request, 'plants/plant_confirm_delete.html', {'plant': plant, 'garden': garden})

@login_required
def plant_type_add_view(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        if name:
            PlantType.objects.get_or_create(name=name)
            return redirect('plant_type_list')
    return render(request, 'plants/plant_type_form.html')

@login_required
def plant_type_list_view(request):
    plant_types = PlantType.objects.all()
    return render(request, 'plants/plant_type_list.html', {'plant_types': plant_types})

@login_required
def plant_type_delete_view(request, type_id):
    plant_type = get_object_or_404(PlantType, id=type_id)
    if request.method == 'POST':
        plant_type.delete()
        return redirect('plant_type_list')
    return render(request, 'plants/plant_type_confirm_delete.html', {'plant_type': plant_type})

@login_required
def plant_recommendations_view(request, plant_id):
    plant = get_object_or_404(Plant, id=plant_id)
    # Permission check: user must have access to the garden
    if not (plant.garden.owner == request.user or request.user in plant.garden.users_with_access.all()):
        return redirect('dashboard')
    recommendations = plant.recommendations.all().order_by('-created_at')
    return render(request, 'plants/plant_recommendations.html', {
        'plant': plant,
        'recommendations': recommendations,
    })