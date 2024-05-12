# Generated by Django 4.1.10 on 2024-03-18 16:02

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DataSet',
            fields=[
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='Creating time.')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='Change time.')),
                ('id', models.UUIDField(default=uuid.uuid1, editable=False, primary_key=True, serialize=False, verbose_name='The key.id')),
                ('name', models.CharField(max_length=150, verbose_name='Name of data')),
                ('desc', models.CharField(max_length=256, verbose_name='Database Description')),
                ('type', models.CharField(choices=[('0', 'General Types'), ('1', 'webType of site')], default='0', max_length=1, verbose_name='Type of')),
                ('meta', models.JSONField(default=dict, verbose_name='The data')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='users.user', verbose_name='The User')),
            ],
            options={
                'db_table': 'dataset',
            },
        ),
        migrations.CreateModel(
            name='Document',
            fields=[
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='Creating time.')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='Change time.')),
                ('id', models.UUIDField(default=uuid.uuid1, editable=False, primary_key=True, serialize=False, verbose_name='The key.id')),
                ('name', models.CharField(max_length=150, verbose_name='Name of documentation')),
                ('char_length', models.IntegerField(verbose_name='Number of documents. The remaining field.')),
                ('status', models.CharField(choices=[('0', 'In the import.'), ('1', 'has completed'), ('2', 'Introduction Failure')], default='0', max_length=1, verbose_name='state of')),
                ('is_active', models.BooleanField(default=True)),
                ('type', models.CharField(choices=[('0', 'General Types'), ('1', 'webType of site')], default='0', max_length=1, verbose_name='Type of')),
                ('meta', models.JSONField(default=dict, verbose_name='The data')),
                ('dataset', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='dataset.dataset')),
            ],
            options={
                'db_table': 'document',
            },
        ),
        migrations.CreateModel(
            name='Paragraph',
            fields=[
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='Creating time.')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='Change time.')),
                ('id', models.UUIDField(default=uuid.uuid1, editable=False, primary_key=True, serialize=False, verbose_name='The key.id')),
                ('content', models.CharField(max_length=4096, verbose_name='Contents of paragraph')),
                ('title', models.CharField(default='', max_length=256, verbose_name='The title')),
                ('status', models.CharField(choices=[('0', 'In the import.'), ('1', 'has completed'), ('2', 'Introduction Failure')], default='0', max_length=1, verbose_name='state of')),
                ('hit_num', models.IntegerField(default=0, verbose_name='Number of fate.')),
                ('is_active', models.BooleanField(default=True)),
                ('dataset', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='dataset.dataset')),
                ('document', models.ForeignKey(db_constraint=False, on_delete=django.db.models.deletion.DO_NOTHING, to='dataset.document')),
            ],
            options={
                'db_table': 'paragraph',
            },
        ),
        migrations.CreateModel(
            name='Problem',
            fields=[
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='Creating time.')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='Change time.')),
                ('id', models.UUIDField(default=uuid.uuid1, editable=False, primary_key=True, serialize=False, verbose_name='The key.id')),
                ('content', models.CharField(max_length=256, verbose_name='The content of the question')),
                ('hit_num', models.IntegerField(default=0, verbose_name='Number of fate.')),
                ('dataset', models.ForeignKey(db_constraint=False, on_delete=django.db.models.deletion.DO_NOTHING, to='dataset.dataset')),
            ],
            options={
                'db_table': 'problem',
            },
        ),
        migrations.CreateModel(
            name='ProblemParagraphMapping',
            fields=[
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='Creating time.')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='Change time.')),
                ('id', models.UUIDField(default=uuid.uuid1, editable=False, primary_key=True, serialize=False, verbose_name='The key.id')),
                ('dataset', models.ForeignKey(db_constraint=False, on_delete=django.db.models.deletion.DO_NOTHING, to='dataset.dataset')),
                ('document', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='dataset.document')),
                ('paragraph', models.ForeignKey(db_constraint=False, on_delete=django.db.models.deletion.DO_NOTHING, to='dataset.paragraph')),
                ('problem', models.ForeignKey(db_constraint=False, on_delete=django.db.models.deletion.DO_NOTHING, to='dataset.problem')),
            ],
            options={
                'db_table': 'problem_paragraph_mapping',
            },
        ),
    ]
