from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Group(models.Model):
    title = models.CharField('Наименование сообщества',
                             max_length=200,
                             help_text='Напишите имя сообщества')
    slug = models.SlugField('Slug сообщества', unique=True,
                            help_text=('Slug сообщества, заполняется'
                                       ' автоматом'))
    description = models.TextField('Описание сообщества!')

    def __str__(self):
        return self.title
