from django.db import models

# Create your models here.
class Booking(models.Model):   
    date_booking = models.DateTimeField()
    date_start = models.DateTimeField()
    date_end = models.DateTimeField()
    value = models.IntegerField()
    status = models.CharField(max_length=30, default='Reservado')
    customer = models.ForeignKey('customers.Customer', on_delete=models.CASCADE)

def __str__(self):
    return self.value
