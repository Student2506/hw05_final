# Generated by Django 2.2.6 on 2021-06-08 13:42

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(help_text='Напишите имя сообщества', max_length=200, verbose_name='Наименование сообщества')),
                ('slug', models.SlugField(help_text='Slug сообщества, заполняется автоматом', unique=True, verbose_name='Slug сообщества')),
                ('description', models.TextField(verbose_name='Описание сообщества!')),
            ],
        ),
    ]
