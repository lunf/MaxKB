# Generated by Django 4.1.13 on 2024-04-28 18:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('setting', '0003_model_meta_model_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='model',
            name='credential',
            field=models.CharField(max_length=102400, verbose_name='Model Certification Information'),
        ),
    ]
