# Generated by Django 4.1.13 on 2024-04-24 15:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dataset', '0002_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='hit_handling_method',
            field=models.CharField(choices=[('optimization', 'Models optimized'), ('directly_return', 'Return directly.')], default='optimization', max_length=20, verbose_name='Method of Treatment'),
        ),
    ]
