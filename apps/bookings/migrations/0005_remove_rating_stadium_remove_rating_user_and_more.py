# Generated by Django 5.2 on 2025-04-07 14:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bookings', '0004_alter_booking_phone_add'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='rating',
            name='stadium',
        ),
        migrations.RemoveField(
            model_name='rating',
            name='user',
        ),
        migrations.RemoveField(
            model_name='wishlist',
            name='stadium',
        ),
        migrations.RemoveField(
            model_name='wishlist',
            name='user',
        ),
        migrations.DeleteModel(
            name='Like',
        ),
        migrations.DeleteModel(
            name='Rating',
        ),
        migrations.DeleteModel(
            name='Wishlist',
        ),
    ]
