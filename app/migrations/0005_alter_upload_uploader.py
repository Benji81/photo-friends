# Generated by Django 3.2.8 on 2022-06-06 13:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_alter_upload_thumbnail'),
    ]

    operations = [
        migrations.AlterField(
            model_name='upload',
            name='uploader',
            field=models.CharField(max_length=64, verbose_name='Name'),
        ),
    ]
