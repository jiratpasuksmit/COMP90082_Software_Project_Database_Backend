# Generated by Django 3.0.6 on 2021-04-30 02:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('jira', '0006_individualcontributions'),
    ]

    operations = [
        migrations.RenameField(
            model_name='individualcontributions',
            old_name='done',
            new_name='done_count',
        ),
    ]
