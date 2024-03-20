# Generated by Django 3.2.16 on 2024-03-18 21:18

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0004_alter_recipe_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(max_length=150, unique=True, validators=[django.core.validators.RegexValidator(message='Имя пользователя может содержатьтолько буквы, цифры и @/./+/-/_.', regex='^[\\w.@+-]+\\Z')], verbose_name='Имя пользователя'),
        ),
    ]
