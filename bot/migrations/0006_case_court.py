# Generated by Django 4.2.4 on 2023-08-24 14:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0005_alter_entity_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='case',
            name='court',
            field=models.CharField(blank=True, max_length=40, null=True, verbose_name='Court'),
        ),
    ]
