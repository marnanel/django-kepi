# Generated by Django 3.0.4 on 2020-04-15 16:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('trilby_api', '0004_auto_20200415_1506'),
    ]

    operations = [
        migrations.AlterField(
            model_name='status',
            name='account',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='poster', to='trilby_api.Person'),
        ),
    ]
