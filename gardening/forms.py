from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils import timezone
from gardening.models import Garden, Plant, PlantType, Note

class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        label='E-mail',
        error_messages={'required': 'E-mail je povinný.'}
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class GardenForm(forms.ModelForm):
    class Meta:
        model = Garden
        fields = ['name', 'description', 'image', 'users_with_access']
        widgets = {
            'users_with_access': forms.CheckboxSelectMultiple,
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['users_with_access'].queryset = User.objects.exclude(id=user.id)

class PlantForm(forms.ModelForm):
    plant_type_name = forms.CharField(
        max_length=100,
        required=True,
        label="Plant Type",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Plant
        fields = ['name', 'planted_date', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'planted_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        plant_type_name = cleaned_data.get('plant_type_name', '').strip()
        planted_date = cleaned_data.get('planted_date')

        # Validate planted_date
        if not planted_date:
            self.add_error('planted_date', "Planted date is required.")
        elif planted_date > timezone.now().date():
            self.add_error('planted_date', "Planted date cannot be in the future.")

        # Handle plant type creation or reuse
        if plant_type_name:
            plant_type_obj, created = PlantType.objects.get_or_create(name=plant_type_name)
            cleaned_data['plant_type'] = plant_type_obj
        else:
            self.add_error('plant_type_name', "Please enter a plant type.")

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.plant_type = self.cleaned_data['plant_type']
        if commit:
            instance.save()
        return instance
    
class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ['content', 'image', 'plant']
        widgets = {
            'plant': forms.CheckboxSelectMultiple,
        }