# Generated by Django 5.0.4 on 2024-04-18 10:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('User', '0008_alter_userprofile_user'),
    ]

    operations = [
        migrations.DeleteModel(
            name='User',
        ),
    ]
