# Generated by Django 3.2.9 on 2021-12-05 08:48

from django.db import migrations
import django.db.models.manager


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0004_alter_productvariant_product'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='productvariant',
            managers=[
                ('object', django.db.models.manager.Manager()),
            ],
        ),
    ]
