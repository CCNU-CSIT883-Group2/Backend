# Generated by Django 5.1.2 on 2024-11-05 10:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("User", "0002_alter_usermodel_role_usermodel_role_check"),
    ]

    operations = [
        migrations.AlterField(
            model_name="usermodel",
            name="role",
            field=models.CharField(max_length=10),
        ),
    ]