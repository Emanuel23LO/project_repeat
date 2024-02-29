from django.db import models

class Booking_cabin(models.Model):
    booking = models.ForeignKey('bookings.Booking', on_delete=models.DO_NOTHING)
    cabin = models.ForeignKey('cabins.Cabin', on_delete=models.DO_NOTHING)
    value = models.FloatField()

def __str__(self):
    return self.value
