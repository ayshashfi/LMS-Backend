# Generated by Django 5.1.3 on 2024-11-17 15:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0014_department_customuser_manager_customuser_department'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='leave_balance',
            field=models.IntegerField(default=0),
        ),
    ]
