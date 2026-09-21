import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('donor', '0004_ngorequirement_donationallocation'),
    ]

    operations = [
        migrations.CreateModel(
            name='PickupRequest',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                (
                    'pickup_address',
                    models.TextField(),
                ),
                (
                    'scheduled_time',
                    models.DateTimeField(),
                ),
                (
                    'notes',
                    models.TextField(blank=True, default=''),
                ),
                (
                    'status',
                    models.CharField(
                        choices=[
                            ('Pending',    'Pending'),
                            ('Confirmed',  'Confirmed'),
                            ('Dispatched', 'Dispatched'),
                            ('Delivered',  'Delivered'),
                            ('Cancelled',  'Cancelled'),
                        ],
                        default='Pending',
                        max_length=20,
                    ),
                ),
                (
                    'created_at',
                    models.DateTimeField(auto_now_add=True),
                ),
                (
                    'updated_at',
                    models.DateTimeField(auto_now=True),
                ),
                (
                    'allocation',
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='pickup_request',
                        to='donor.donationallocation',
                    ),
                ),
            ],
        ),
    ]
