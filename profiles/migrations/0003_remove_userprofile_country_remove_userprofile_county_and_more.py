# Generated by Django 4.0.2 on 2022-02-21 23:27

from django.db import migrations, models
import django.db.models.deletion
import django_countries.fields


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0002_remove_userprofile_email_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='country',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='county',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='phone_number',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='postcode',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='street_address1',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='street_address2',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='town_or_city',
        ),
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('default', models.BooleanField(default=False)),
                ('phone_number', models.CharField(max_length=20)),
                ('street_address1', models.CharField(max_length=80)),
                ('street_address2', models.CharField(blank=True, max_length=80, null=True)),
                ('town_or_city', models.CharField(max_length=40)),
                ('county', models.CharField(blank=True, max_length=80, null=True)),
                ('postcode', models.CharField(blank=True, max_length=20, null=True)),
                ('country', django_countries.fields.CountryField(max_length=2)),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='profiles.userprofile')),
            ],
        ),
    ]
