# Generated migration for custom fields

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('admin_panel', '0002_systemsettings_license_code_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomField',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Field Name')),
                ('label', models.CharField(max_length=200, verbose_name='Display Label')),
                ('field_type', models.CharField(choices=[('text', 'Text Field'), ('textarea', 'Text Area'), ('number', 'Number'), ('email', 'Email'), ('url', 'URL'), ('date', 'Date'), ('datetime', 'Date & Time'), ('boolean', 'Yes/No'), ('select', 'Dropdown'), ('multiselect', 'Multiple Selection')], max_length=20, verbose_name='Field Type')),
                ('target_model', models.CharField(choices=[('user', 'User/Customer'), ('ticket', 'Ticket'), ('company', 'Company/Organization')], max_length=20, verbose_name='Target Model')),
                ('is_required', models.BooleanField(default=False, verbose_name='Required')),
                ('default_value', models.TextField(blank=True, null=True, verbose_name='Default Value')),
                ('help_text', models.TextField(blank=True, null=True, verbose_name='Help Text')),
                ('choices', models.TextField(blank=True, help_text='For dropdown/multiselect fields, enter one option per line', null=True, verbose_name='Choices (one per line)')),
                ('is_visible_in_list', models.BooleanField(default=False, verbose_name='Visible in List View')),
                ('is_searchable', models.BooleanField(default=False, verbose_name='Searchable')),
                ('display_order', models.IntegerField(default=0, verbose_name='Display Order')),
                ('visible_to_customers', models.BooleanField(default=True, verbose_name='Visible to Customers')),
                ('editable_by_customers', models.BooleanField(default=True, verbose_name='Editable by Customers')),
                ('is_active', models.BooleanField(default=True, verbose_name='Active')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated at')),
            ],
            options={
                'verbose_name': 'Custom Field',
                'verbose_name_plural': 'Custom Fields',
                'ordering': ['target_model', 'display_order', 'name'],
            },
        ),
        migrations.CreateModel(
            name='CustomFieldValue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('object_id', models.PositiveIntegerField(verbose_name='Object ID')),
                ('value', models.TextField(blank=True, null=True, verbose_name='Value')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='created at')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='updated at')),
                ('field', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='values', to='admin_panel.customfield')),
            ],
            options={
                'verbose_name': 'Custom Field Value',
                'verbose_name_plural': 'Custom Field Values',
            },
        ),
        migrations.AlterUniqueTogether(
            name='customfield',
            unique_together={('name', 'target_model')},
        ),
        migrations.AlterUniqueTogether(
            name='customfieldvalue',
            unique_together={('field', 'object_id')},
        ),
    ]