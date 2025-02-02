# Generated by Django 5.0.4 on 2024-04-15 00:04

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='eBook',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('author', models.CharField(max_length=100)),
                ('description', models.TextField()),
                ('publication_date', models.DateField()),
                ('content', models.CharField(max_length=2000, validators=[django.core.validators.URLValidator()])),
                ('cover', models.CharField(max_length=2000, validators=[django.core.validators.URLValidator()])),
            ],
        ),
        migrations.CreateModel(
            name='eBookCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='eBook.category')),
                ('ebook', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='eBook.ebook')),
            ],
        ),
    ]
