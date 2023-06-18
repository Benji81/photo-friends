# Generated by Django 3.2.8 on 2021-11-14 16:48

from django.db import migrations, models

import app.models


class Migration(migrations.Migration):
    dependencies = [
        ("app", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="upload",
            name="uploaded_at",
            field=models.DateTimeField(
                default=app.models.get_utc_now,
                help_text="Date in format ISO8601. Example: 2020-03-03T18:31:01.915000Z.",
            ),
        ),
        migrations.AlterField(
            model_name="album",
            name="creator",
            field=models.CharField(max_length=64, verbose_name="Creator"),
        ),
        migrations.AlterField(
            model_name="album",
            name="name",
            field=models.CharField(max_length=64, verbose_name="Album name"),
        ),
        migrations.AlterField(
            model_name="upload",
            name="created_at",
            field=models.DateTimeField(
                blank=True,
                db_index=True,
                help_text="Date in format ISO8601. Example: 2020-03-03T18:31:01.915000Z.",
                null=True,
            ),
        ),
    ]
