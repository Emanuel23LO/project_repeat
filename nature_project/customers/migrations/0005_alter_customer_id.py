# Generated by Django 5.0.1 on 2024-02-05 17:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('customers', '0004_auto_20240205_1109'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='id',
            field=models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID'),
        ),
    ]
