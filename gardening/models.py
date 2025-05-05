from django.contrib.auth.models import User
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.timezone import now

# Funkce pro validaci, že datum není v budoucnosti
def validate_not_future_date(value):
    if value > now().date():
        raise ValidationError('Datum nemůže být v budoucnosti.')

# Tabulka pro jednotlivé zahrádky
class Garden(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name='Název zahrádky',
        help_text='Zadejte název zahrádky'
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Popis zahrádky',
        help_text='Zadejte popis zahrádky (volitelné)'
    )
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='owned_gardens',
        verbose_name='Vlastník zahrádky',
        help_text='Vyberte vlastníka zahrádky'
    )
    users_with_access = models.ManyToManyField(
        User,
        related_name='accessible_gardens',
        blank=True,
        verbose_name='Uživatelé s přístupem',
        help_text='Vyberte uživatele, kteří mají přístup k zahrádce'
    )
    image = models.ImageField(
        upload_to='gardens/',
        blank=True,
        null=True,
        verbose_name='Obrázek zahrádky',
        help_text='Nahrajte obrázek zahrádky (volitelné)'
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Zahrádka'
        verbose_name_plural = 'Zahrádky'

    def __str__(self):
        return self.name

# Tabulka pro typy rostlin
class PlantType(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Typ rostliny',
        help_text='Zadejte typ rostliny (např. Rajčata, Mrkev)'
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Typ rostliny'
        verbose_name_plural = 'Typy rostlin'

    def __str__(self):
        return self.name


# Tabulky pro jednotlivé rostliny
class Plant(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name='Název rostliny',
        help_text='Zadejte název rostliny'
    )
    plant_type = models.ForeignKey(
        PlantType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='plants',
        verbose_name='Typ rostliny',
        help_text='Vyberte typ rostliny (volitelné)'
    )
    garden = models.ForeignKey(
        Garden,
        on_delete=models.CASCADE,
        related_name='plants',
        verbose_name='Zahrádka',
        help_text='Vyberte zahrádku, do které rostlina patří'
    )
    planted_date = models.DateField(
        blank=True,
        null=True,
        validators=[validate_not_future_date],
        verbose_name='Datum zasazení',
        help_text='Zadejte datum, kdy byla rostlina zasazena (volitelné)'
    )
    image = models.ImageField(
        upload_to='plants/',
        blank=True,
        null=True,
        verbose_name='Obrázek rostliny',
        help_text='Nahrajte obrázek rostliny (volitelné)'
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Rostlina'
        verbose_name_plural = 'Rostliny'

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        verbose_name = 'Rostlina'
        verbose_name_plural = 'Rostliny'

    def __str__(self):
        return self.name

# Tabulka pro poznámky k jednotlivým rostlinám
class Note(models.Model):
    plant = models.ManyToManyField(
        Plant,
        related_name='notes',
        verbose_name='Rostliny',
        help_text='Vyberte rostliny, ke kterým poznámka patří'
    )
    date = models.DateField(
        auto_now_add=True,
        verbose_name='Datum poznámky',
        help_text='Datum, kdy byla poznámka vytvořena'
    )
    content = models.TextField(
        verbose_name='Obsah poznámky',
        help_text='Zadejte obsah poznámky'
    )
    image = models.ImageField(
        upload_to='notes/',
        blank=True,
        null=True,
        verbose_name='Obrázek poznámky',
        help_text='Nahrajte obrázek k poznámce (volitelné)'
    )

    class Meta:
        ordering = ['-date']
        verbose_name = 'Poznámka'
        verbose_name_plural = 'Poznámky'

    def __str__(self):
        return f"Note for {', '.join([p.name for p in self.plant.all()])} on {self.date}"


# Tabulka pro AI doporučení k jednotlivým rostlinám
class AIRecommendation(models.Model):
    plant = models.ForeignKey(
        Plant,
        on_delete=models.CASCADE,
        related_name='recommendations',
        verbose_name='Rostlina',
        help_text='Vyberte rostlinu, ke které doporučení patří'
    )
    recommendation = models.TextField(
        verbose_name='Doporučení',
        help_text='Zadejte doporučení pro rostlinu'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Datum vytvoření',
        help_text='Datum, kdy bylo doporučení vytvořeno'
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'AI Doporučení'
        verbose_name_plural = 'AI Doporučení'

    def __str__(self):
        return f"Doporučení pro {self.plant.name} z {self.created_at}"