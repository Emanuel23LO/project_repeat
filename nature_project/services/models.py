from django.db import models

class Service(models.Model):
    name = models.CharField(max_length=50, unique=True)
    value = models.IntegerField()
    image = models.ImageField(upload_to='static/service_images', null=True)
    status = models.BooleanField(default=True)

def __str__(self):
    return self.name
