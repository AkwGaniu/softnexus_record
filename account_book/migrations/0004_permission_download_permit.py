# Generated by Django 3.0.8 on 2020-07-21 12:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account_book', '0003_auto_20200714_0831'),
    ]

    operations = [
        migrations.AddField(
            model_name='permission',
            name='download_permit',
            field=models.BooleanField(default=False),
        ),
    ]