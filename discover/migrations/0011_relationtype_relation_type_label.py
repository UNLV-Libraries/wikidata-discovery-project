# Generated by Django 4.1.8 on 2023-04-25 18:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('discover', '0010_relationtype'),
    ]

    operations = [
        migrations.AddField(
            model_name='relationtype',
            name='relation_type_label',
            field=models.CharField(max_length=50, null=True),
        ),
    ]