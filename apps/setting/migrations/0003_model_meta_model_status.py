# Generated by Django 4.1.13 on 2024-03-22 17:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('setting', '0002_systemsetting'),
    ]

    operations = [
        migrations.AddField(
            model_name='model',
            name='meta',
            field=models.JSONField(default=dict, verbose_name='Model of data,Used for storage downloads,or wrong information.'),
        ),
        migrations.AddField(
            model_name='model',
            name='status',
            field=models.CharField(choices=[('SUCCESS', 'Successful'), ('ERROR', 'Failure'), ('DOWNLOAD', 'Downloads')], default='SUCCESS', max_length=20, verbose_name='Set the type.'),
        ),
    ]
