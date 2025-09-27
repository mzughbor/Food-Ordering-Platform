from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Restaurant(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, default='')
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='restaurants')
    location = models.CharField(max_length=255, blank=True, default='')
    logo = models.ImageField(upload_to='restaurant_logos/', blank=True, null=True, help_text='Restaurant logo or image')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
