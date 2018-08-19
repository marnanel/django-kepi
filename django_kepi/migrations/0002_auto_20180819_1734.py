# Generated by Django 2.0.6 on 2018-08-19 17:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('django_kepi', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Register',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.PositiveIntegerField()),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType')),
            ],
        ),
        migrations.AddField(
            model_name='accept',
            name='register',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='django_kepi.Register'),
        ),
        migrations.AddField(
            model_name='add',
            name='register',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='django_kepi.Register'),
        ),
        migrations.AddField(
            model_name='create',
            name='register',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='django_kepi.Register'),
        ),
        migrations.AddField(
            model_name='delete',
            name='register',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='django_kepi.Register'),
        ),
        migrations.AddField(
            model_name='follow',
            name='register',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='django_kepi.Register'),
        ),
        migrations.AddField(
            model_name='like',
            name='register',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='django_kepi.Register'),
        ),
        migrations.AddField(
            model_name='reject',
            name='register',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='django_kepi.Register'),
        ),
        migrations.AddField(
            model_name='remove',
            name='register',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='django_kepi.Register'),
        ),
        migrations.AddField(
            model_name='tombstone',
            name='register',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='django_kepi.Register'),
        ),
        migrations.AddField(
            model_name='undo',
            name='register',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='django_kepi.Register'),
        ),
        migrations.AddField(
            model_name='update',
            name='register',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='django_kepi.Register'),
        ),
    ]
