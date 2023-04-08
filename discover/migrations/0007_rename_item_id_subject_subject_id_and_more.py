# Generated by Django 4.1.5 on 2023-04-04 13:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('discover', '0006_corp_oralhistory_subject'),
    ]

    operations = [
        migrations.RenameField(
            model_name='subject',
            old_name='item_id',
            new_name='subject_id',
        ),
        migrations.RenameField(
            model_name='subject',
            old_name='itemlabel',
            new_name='subjectlabel',
        ),
        migrations.AddField(
            model_name='collection',
            name='donatedby_id',
            field=models.CharField(max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='collection',
            name='donatedbylabel',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='collection',
            name='subject_id',
            field=models.CharField(max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='collection',
            name='subjectlabel',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
