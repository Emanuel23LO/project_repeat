from django.db import models

class Cabin(models.Model):
    name = models.CharField(max_length=200, unique=True)
    capacity= models.IntegerField()
    description= models.CharField(max_length=300)
    value = models.IntegerField()
    image = models.ImageField(upload_to='static/services_images', null=True)
    cabin_type = models.ForeignKey('cabin_types.Cabin_type', on_delete=models.DO_NOTHING)
    status = models.BooleanField(default=True)

def __str__(self):
    return self.name

