# Generated by Django 5.1.2 on 2025-02-05 02:55

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0004_voter_auth_voter_candidate_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='election',
            name='NUM_OFFICES',
        ),
        migrations.RemoveField(
            model_name='election',
            name='YEAR',
        ),
        migrations.RemoveField(
            model_name='office',
            name='DIGIT_NUM',
        ),
        migrations.AlterField(
            model_name='election',
            name='END_ELECTION',
            field=models.DateTimeField(default=datetime.datetime(2025, 2, 5, 2, 55, 51, 472238, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='election',
            name='END_SETTING',
            field=models.DateTimeField(default=datetime.datetime(2025, 2, 5, 2, 55, 51, 472198, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='voter',
            name='PUB_KEY',
            field=models.TextField(),
        ),
    ]
