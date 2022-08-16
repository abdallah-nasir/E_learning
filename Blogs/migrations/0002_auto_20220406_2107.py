# Generated by Django 3.2.8 on 2022-04-06 21:07

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import taggit.managers


class Migration(migrations.Migration):

    dependencies = [
        ('taggit', '0004_auto_20220406_2107'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Blogs', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='blog',
            name='category',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='Blogs.category'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='blog',
            name='comments',
            field=models.ManyToManyField(blank=True, related_name='blog_comments', to='Blogs.Blog_Comment'),
        ),
        migrations.AddField(
            model_name='blog',
            name='image',
            field=models.ManyToManyField(blank=True, related_name='blog_comment', to='Blogs.Blog_Images'),
        ),
        migrations.AddField(
            model_name='blog',
            name='tags',
            field=taggit.managers.TaggableManager(help_text='A comma-separated list of tags.', through='taggit.TaggedItem', to='taggit.Tag', verbose_name='Tags'),
        ),
        migrations.AddField(
            model_name='blog',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='accounts.user'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='blog',
            name='viewers',
            field=models.ManyToManyField(blank=True, related_name='blog_viewers', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='blog_comment',
            name='blog',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='blog_comment', to='Blogs.blog'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='blog_comment',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='accounts.user'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='blog_comment_reply',
            name='blog',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='blog_comment_reply', to='Blogs.blog'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='blog_comment_reply',
            name='comment',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='Blogs.blog_comment'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='blog_comment_reply',
            name='user',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='accounts.user'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='blog_images',
            name='blog',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='Blogs.blog'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='blog_payment',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
    ]