# Generated by Django 4.2.13 on 2024-06-18 18:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('php', '0002_userprofile_secret_word'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='secret_word',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
