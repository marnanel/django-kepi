# Generated by Django 3.0.9 on 2020-09-20 22:51

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('bowler_pub', '0003_incomingmessage'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='incomingmessage',
            name='is_local_user',
        ),
    ]