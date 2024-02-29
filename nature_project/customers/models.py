from django.db import models

class Customer(models.Model):
    full_name = models.CharField(max_length=255)
    document = models.IntegerField(unique=True)
    phone = models.IntegerField()
    email = models.EmailField(max_length=300)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.full_name
    
