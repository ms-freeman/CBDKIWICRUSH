# Generated by Django 4.1.7 on 2023-08-20 19:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0011_blogarticle_navigationitem'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cart',
            name='total',
        ),
    ]
