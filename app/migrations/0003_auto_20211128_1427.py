# Generated by Django 3.2.8 on 2021-11-28 14:27

from django.db import migrations, models

import app.models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0002_auto_20211114_1648"),
    ]

    operations = [
        migrations.AlterField(
            model_name="upload",
            name="photo",
            field=models.ImageField(
                help_text="Select one or more images to upload",
                upload_to=app.models.get_upload_path,
                verbose_name="Image to upload",
            ),
        ),
        migrations.AlterField(
            model_name="upload",
            name="uploader",
            field=models.CharField(
                help_text="Your name", max_length=64, verbose_name="Name"
            ),
        ),
    ]