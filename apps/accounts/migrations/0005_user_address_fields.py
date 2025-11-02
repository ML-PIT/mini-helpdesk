# Generated migration for address fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_merge_20251022_1153'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='street',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='street'),
        ),
        migrations.AddField(
            model_name='user',
            name='postal_code',
            field=models.CharField(blank=True, max_length=10, null=True, verbose_name='postal code'),
        ),
        migrations.AddField(
            model_name='user',
            name='city',
            field=models.CharField(blank=True, max_length=100, null=True, verbose_name='city'),
        ),
        migrations.AddField(
            model_name='user',
            name='country',
            field=models.CharField(blank=True, default='Deutschland', max_length=100, null=True, verbose_name='country'),
        ),
    ]