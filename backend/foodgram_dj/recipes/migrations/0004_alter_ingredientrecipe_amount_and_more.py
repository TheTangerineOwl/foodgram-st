# Generated by Django 5.2.1 on 2025-06-12 04:31

import django.core.validators
import recipes.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_alter_ingredientrecipe_options_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredientrecipe',
            name='amount',
            field=models.PositiveIntegerField(validators=[recipes.models.validate_positive, django.core.validators.MinValueValidator(1, message='Значение должно быть больше нуля!')], verbose_name='Количество'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='cooking_time',
            field=models.PositiveSmallIntegerField(validators=[recipes.models.validate_positive, django.core.validators.MinValueValidator(1, message='Значение должно быть больше нуля!')], verbose_name='Время приготовления (в минутах)'),
        ),
        migrations.AlterField(
            model_name='recipe',
            name='image',
            field=models.ImageField(upload_to='recipes/images', verbose_name='Фото'),
        ),
    ]
