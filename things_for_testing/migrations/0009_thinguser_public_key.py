# Generated by Django 2.1.5 on 2019-05-05 18:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('things_for_testing', '0008_thingnote_owner'),
    ]

    operations = [
        migrations.AddField(
            model_name='thinguser',
            name='public_key',
            field=models.CharField(default='', max_length=256),
            preserve_default=False,
        ),
    ]