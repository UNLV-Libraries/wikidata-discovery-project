# Generated by Django 4.1.5 on 2023-04-20 20:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('discover', '0006_remove_corpbody_collection_id_corpbody_collection_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='corpbody',
            name='instanceof_id',
            field=models.CharField(max_length=20, null=True),
        ),
    ]
