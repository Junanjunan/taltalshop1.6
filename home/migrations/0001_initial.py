# Generated by Django 4.0.6 on 2022-07-23 14:02

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MainPhoto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item_category', models.CharField(choices=[('shampoo', '샴푸'), ('black_powder', '흑채'), ('wig', '가발'), ('hairbeam', '헤어빔')], max_length=30)),
                ('main_photo', models.ImageField(upload_to='main_photo')),
                ('name', models.CharField(max_length=100)),
            ],
        ),
    ]
