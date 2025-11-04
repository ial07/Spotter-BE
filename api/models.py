from django.db import models
from django.contrib.auth.models import User
import json

class DriverLogbook(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    logbook_data = models.JSONField(default=list)  # menyimpan semua events
