# Generated by Django 4.1.10 on 2024-03-18 16:02

import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion
import uuid


def insert_default_data(apps, schema_editor):
    TeamModel = apps.get_model('setting', 'Team')
    TeamModel.objects.create(user_id='f0dd8f71-e4ee-11ee-8c84-a8a1595801ab', name='The admin team.')


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Team',
            fields=[
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='Creating time.')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='Change time.')),
                ('user',
                 models.OneToOneField(on_delete=django.db.models.deletion.DO_NOTHING, primary_key=True, serialize=False,
                                      to='users.user', verbose_name='The team owners.')),
                ('name', models.CharField(max_length=128, verbose_name='The Team Name')),
            ],
            options={
                'db_table': 'team',
            },
        ),
        migrations.RunPython(insert_default_data),
        migrations.CreateModel(
            name='TeamMember',
            fields=[
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='Creating time.')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='Change time.')),
                ('id', models.UUIDField(default=uuid.uuid1, editable=False, primary_key=True, serialize=False,
                                        verbose_name='The key.id')),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='setting.team',
                                           verbose_name='The teamid')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='users.user',
                                           verbose_name='Member Usersid')),
            ],
            options={
                'db_table': 'team_member',
            },
        ),
        migrations.CreateModel(
            name='TeamMemberPermission',
            fields=[
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='Creating time.')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='Change time.')),
                ('id', models.UUIDField(default=uuid.uuid1, editable=False, primary_key=True, serialize=False,
                                        verbose_name='The key.id')),
                ('auth_target_type',
                 models.CharField(choices=[('DATASET', 'The data collection'), ('APPLICATION', 'Applications')], default='DATASET',
                                  max_length=128, verbose_name='Authorized objectives')),
                ('target', models.UUIDField(verbose_name='The data collection/Applicationsid')),
                ('operate', django.contrib.postgres.fields.ArrayField(
                    base_field=models.CharField(blank=True, choices=[('MANAGE', 'management'), ('USE', 'Use of')],
                                                default='USE', max_length=256), size=None,
                    verbose_name='Authorization operating list')),
                ('member', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='setting.teammember',
                                             verbose_name='Members of Team')),
            ],
            options={
                'db_table': 'team_member_permission',
            },
        ),
        migrations.CreateModel(
            name='Model',
            fields=[
                ('create_time', models.DateTimeField(auto_now_add=True, verbose_name='Creating time.')),
                ('update_time', models.DateTimeField(auto_now=True, verbose_name='Change time.')),
                ('id', models.UUIDField(default=uuid.uuid1, editable=False, primary_key=True, serialize=False,
                                        verbose_name='The key.id')),
                ('name', models.CharField(max_length=128, verbose_name='The name')),
                ('model_type', models.CharField(max_length=128, verbose_name='Type of Model')),
                ('model_name', models.CharField(max_length=128, verbose_name='Name of model')),
                ('provider', models.CharField(max_length=128, verbose_name='Suppliers')),
                ('credential', models.CharField(max_length=5120, verbose_name='Model Certification Information')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='users.user',
                                           verbose_name='Member Usersid')),
            ],
            options={
                'db_table': 'model',
                'unique_together': {('name', 'user_id')},
            },
        ),
    ]
