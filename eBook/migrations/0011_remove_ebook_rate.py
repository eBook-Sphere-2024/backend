# Generated by Django 5.0.4 on 2024-05-20 03:11

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('eBook', '0010_ebook_rate'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ebook',
            name='rate',
        ),
    ]
