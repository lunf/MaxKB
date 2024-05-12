# Generated by Django 4.1.13 on 2024-04-29 13:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0004_applicationaccesstoken_show_source'),
    ]

    operations = [
        migrations.AlterField(
            model_name='chat',
            name='abstract',
            field=models.CharField(max_length=1024, verbose_name='The summary'),
        ),
        migrations.AlterField(
            model_name='chatrecord',
            name='answer_text',
            field=models.CharField(max_length=40960, verbose_name='The Answer'),
        ),
    ]
