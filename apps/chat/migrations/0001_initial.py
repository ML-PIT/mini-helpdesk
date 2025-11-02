# Generated migration for chat app

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ChatSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('widget_color', models.CharField(default='#667eea', help_text='Hex color code', max_length=7)),
                ('widget_position', models.CharField(choices=[('bottom-right', 'Bottom Right'), ('bottom-left', 'Bottom Left')], default='bottom-right', max_length=20)),
                ('auto_assign', models.BooleanField(default=True, help_text='Automatically assign chats to available agents')),
                ('offline_message', models.TextField(default='Wir sind derzeit offline. Senden Sie uns eine E-Mail und wir melden uns so schnell wie möglich.', help_text='Message shown when no agents are available')),
                ('welcome_message', models.TextField(default='Hallo! Wie können wir Ihnen helfen?', help_text='First message shown to visitors')),
                ('is_enabled', models.BooleanField(default=True)),
                ('business_hours_only', models.BooleanField(default=False)),
                ('business_start', models.TimeField(default='09:00')),
                ('business_end', models.TimeField(default='17:00')),
            ],
            options={
                'verbose_name': 'Chat Settings',
                'verbose_name_plural': 'Chat Settings',
            },
        ),
        migrations.CreateModel(
            name='ChatSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('visitor_name', models.CharField(max_length=100)),
                ('visitor_email', models.EmailField(max_length=254)),
                ('visitor_ip', models.GenericIPAddressField()),
                ('session_id', models.CharField(max_length=100, unique=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('ended_at', models.DateTimeField(blank=True, null=True)),
                ('status', models.CharField(choices=[('waiting', 'Waiting for Agent'), ('active', 'Active Chat'), ('ended', 'Chat Ended')], default='waiting', max_length=20)),
                ('initial_message', models.TextField(help_text="Visitor's first message")),
                ('visitor_page_url', models.URLField(blank=True, help_text='Page where chat was initiated', null=True)),
                ('assigned_agent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='chat_sessions', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='ChatMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('is_from_visitor', models.BooleanField(default=True)),
                ('sender_name', models.CharField(max_length=100)),
                ('message_type', models.CharField(choices=[('text', 'Text Message'), ('system', 'System Message'), ('file', 'File Upload')], default='text', max_length=20)),
                ('agent', models.ForeignKey(blank=True, help_text='If message is from agent', null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='chat.chatsession')),
            ],
            options={
                'ordering': ['timestamp'],
            },
        ),
    ]