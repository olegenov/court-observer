# Generated by Django 4.2.4 on 2023-08-02 00:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0003_rename_name_observation_entity'),
    ]

    operations = [
        migrations.AlterField(
            model_name='case',
            name='link',
            field=models.CharField(max_length=200, verbose_name='Name'),
        ),
    ]
