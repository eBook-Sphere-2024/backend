# Generated by Django 5.0.4 on 2024-04-16 22:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('User', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='profile_image',
            field=models.CharField(max_length=2000),
        ),
    ]
