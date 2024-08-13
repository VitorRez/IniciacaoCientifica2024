# Generated by Django 5.0.6 on 2024-07-13 14:22

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_alter_election_year'),
    ]

    operations = [
        migrations.CreateModel(
            name='Offices',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(default=' ')),
                ('digit_num', models.IntegerField()),
                ('electionid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='electionid_office', to='api.election')),
            ],
            options={
                'unique_together': {('name', 'electionid')},
            },
        ),
    ]
