# Generated by Django 2.0.4 on 2018-05-04 08:58

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Topic',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32, unique=True, verbose_name='话题名')),
                ('info', models.CharField(blank=True, max_length=256, verbose_name='话题描述')),
            ],
        ),
    ]
