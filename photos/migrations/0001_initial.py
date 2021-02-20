# Generated by Django 3.1.7 on 2021-02-20 06:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('rooms', '0002_auto_20210220_1243'),
    ]

    operations = [
        migrations.CreateModel(
            name='Photo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('caption', models.CharField(max_length=200)),
                ('file', models.ImageField(blank=True, upload_to='room_photos')),
                ('room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='photos', to='rooms.room')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
