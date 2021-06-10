from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.deletion import DO_NOTHING
from groups.models import Group

User = get_user_model()


class Post(models.Model):
    text = models.TextField('Текст поста',
                            help_text='Напишите содержание поста'
                            )
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        blank=True,
        related_name='posts',
        null=True,
        help_text='Выберите сообщество (оционально)'
    )
    image = models.ImageField(upload_to='posts/', blank=True, null=True)

    class Meta:
        ordering = ('-pub_date', )

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE,
                             related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField('Текст комментария.',
                            help_text='Напишите текст комментария.')
    created = models.DateTimeField('Дата комментария', auto_now_add=True)

    class Meta:
        ordering = ('-created', )

    def __str__(self):
        return self.text[:15]


class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=DO_NOTHING,
                             related_name='follower')
    author = models.ForeignKey(User, on_delete=DO_NOTHING,
                               related_name='following')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'author'],
                                    name='user_author_constraint')
        ]
