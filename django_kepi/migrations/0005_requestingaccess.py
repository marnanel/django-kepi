# Generated by Django 2.1 on 2018-08-28 08:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('django_kepi', '0004_auto_20180828_0804'),
    ]

    operations = [
        migrations.CreateModel(
            name='RequestingAccess',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('grantor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='grantor', to='django_kepi.Actor')),
                ('hopefuls', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='hopefuls', to='django_kepi.Actor')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
