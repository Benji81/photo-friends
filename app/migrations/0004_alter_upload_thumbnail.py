# Generated by Django 3.2.8 on 2022-06-05 21:43

import app.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_auto_20211128_1427'),
    ]

    operations = [
        migrations.AlterField(
            model_name='upload',
            name='thumbnail',
            field=models.ImageField(editable=False, upload_to=app.models.get_thumbnail_path),
        ),
    ]
