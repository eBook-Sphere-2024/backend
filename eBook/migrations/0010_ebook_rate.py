# Generated by Django 5.0.4 on 2024-04-19 16:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('eBook', '0009_alter_ebook_author'),
    ]

    operations = [
        migrations.AddField(
            model_name='ebook',
            name='rate',
            field=models.IntegerField(default=0),
        ),
    ]
