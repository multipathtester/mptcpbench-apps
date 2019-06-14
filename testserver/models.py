from django.db import models


class PendingTrace(models.Model):
    name = models.CharField(max_length=200)
    full_path = models.CharField(max_length=200)
