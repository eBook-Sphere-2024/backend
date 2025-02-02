# Generated by Django 5.0.4 on 2024-05-06 02:25

import django.db.models.deletion
import django.db.models.expressions
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Comments', '0007_alter_comment_reply_to'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='reply_to',
            field=models.ForeignKey(blank=True, limit_choices_to={'ebook': django.db.models.expressions.OuterRef('ebook')}, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='replies', to='Comments.comment'),
        ),
    ]
