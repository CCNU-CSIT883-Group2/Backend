# Generated by Django 5.1.2 on 2024-11-05 10:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("Questions", "0004_alter_questionsmodel_type_questionsmodel_type_check"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="questionsmodel",
            name="type_check",
        ),
        migrations.AlterField(
            model_name="questionsmodel",
            name="type",
            field=models.CharField(default="", max_length=10),
        ),
        migrations.AddConstraint(
            model_name="questionsmodel",
            constraint=models.CheckConstraint(
                condition=models.Q(("type__in", ["choice", "blank"])),
                name="Questions_type_check",
            ),
        ),
    ]
