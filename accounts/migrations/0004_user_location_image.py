# Generated by Django 5.1.3 on 2024-11-19 04:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_user_address_user_description_user_phone_number_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='location_image',
            field=models.ImageField(blank=True, null=True, upload_to='locations/'),
        ),
    ]
