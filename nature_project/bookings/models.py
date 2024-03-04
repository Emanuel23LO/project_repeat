from django.db import models

class Booking(models.Model):
    date_booking = models.DateTimeField()
    date_start = models.DateTimeField()
    date_end = models.DateTimeField()
    value = models.IntegerField()
    status = models.CharField(max_length=30, default='Reservado')
    customer = models.ForeignKey('customers.Customer', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.id} - {self.customer.full_name} - {self.value}"

    