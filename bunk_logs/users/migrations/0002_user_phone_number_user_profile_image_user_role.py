# Generated by Django 5.0.12 on 2025-03-02 13:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='phone_number',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='profile_image',
            field=models.ImageField(blank=True, null=True, upload_to='profile_images/'),
        ),
        migrations.AddField(
            model_name='user',
            name='role',
            field=models.CharField(choices=[('COUNSELOR', 'Counselor'), ('CAMPER_CARE', 'Camper Care Team'), ('UNIT_HEAD', 'Unit Head'), ('ADMIN', 'Administrator')], default='COUNSELOR', max_length=20),
        ),
    ]
