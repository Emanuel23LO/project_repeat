from django.db import models


class Payment(models.Model):
    payment_method = models.CharField(max_length=255)
    date = models.DateField()
    value = models.FloatField(max_length=50)
    booking = models.ForeignKey('bookings.Booking', on_delete=models.DO_NOTHING)
    status = models.BooleanField(default=True)

def __str__(self):
    return self.value

