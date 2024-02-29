from django.db import models

class Cabin_type(models.Model):
    name = models.CharField(max_length=200, unique=True)
    status = models.BooleanField(default=True)
    

    def __str__(self):
        return self.name