# Generated by Django 4.1.13 on 2024-04-22 19:31

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('dataset', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Image',
            fields=[
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='Creating time.')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='Change time.')),
                ('id', models.UUIDField(default=uuid.uuid1, editable=False, primary_key=True, serialize=False, verbose_name='The key.id')),
                ('image', models.BinaryField(verbose_name='Image data')),
                ('image_name', models.CharField(default='', max_length=256, verbose_name='Name of image')),
            ],
            options={
                'db_table': 'image',
            },
        ),
    ]
