# Generated by Django 2.1.1 on 2018-10-03 14:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('things_for_testing', '0002_thinguser_remote'),
    ]

    operations = [
        migrations.AddField(
            model_name='thingarticle',
            name='remote_url',
            field=models.URLField(default=None, max_length=256, null=True),
        ),
    ]