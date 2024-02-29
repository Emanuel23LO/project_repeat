from django.db import models

class Booking_service(models.Model):
    booking = models.ForeignKey('bookings.Booking', on_delete=models.DO_NOTHING)
    service = models.ForeignKey('services.Service', on_delete=models.DO_NOTHING)
    value = models.FloatField()

def __str__(self):
    return self.value

