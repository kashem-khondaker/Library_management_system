from django.db import models
import uuid

# Create your models here.
class Author(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # Secure and unpredictable ID
    name = models.CharField(max_length=255)
    biography = models.TextField(blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_death = models.DateField(null=True, blank=True)
    nationality = models.CharField(max_length=100, null=True, blank=True)
    image = models.ImageField(upload_to='authors/images/', null=True, blank=True)  # Field for author's picture

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']