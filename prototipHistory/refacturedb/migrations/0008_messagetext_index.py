# Generated by Django 4.2.5 on 2023-09-28 18:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('refacturedb', '0007_remove_messagetext_index'),
    ]

    operations = [
        migrations.AddField(
            model_name='messagetext',
            name='index',
            field=models.BooleanField(default=False),
        ),
    ]
