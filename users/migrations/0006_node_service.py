# Generated by Django 3.0.4 on 2020-03-21 03:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0005_author_create_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='node',
            name='service',
            field=models.URLField(default='https://SERVICE/API', max_length=250),
        ),
    ]
