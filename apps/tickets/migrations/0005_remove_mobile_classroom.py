# Generated migration to remove mobile classroom fields

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0004_merge_20251022_1104'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ticket',
            name='mobile_classroom',
        ),
        migrations.DeleteModel(
            name='MobileClassroom',
        ),
        migrations.DeleteModel(
            name='MobileClassroomLocation',
        ),
    ]