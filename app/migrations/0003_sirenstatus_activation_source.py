# Generated by Django 4.2 on 2025-07-03 23:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='sirenstatus',
            name='activation_source',
            field=models.CharField(default='unknown', max_length=20),
        ),
    ]
