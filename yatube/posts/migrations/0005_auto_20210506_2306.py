# Generated by Django 2.2.6 on 2021-05-06 20:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0003_auto_20210424_1824'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='group',
            field=models.ForeignKey(blank=True, help_text='Выберите сообщество (оционально)', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='posts', to='groups.Group'),
        ),
        migrations.AlterField(
            model_name='post',
            name='text',
            field=models.TextField(help_text='Напишите содержание поста'),
        ),
    ]
