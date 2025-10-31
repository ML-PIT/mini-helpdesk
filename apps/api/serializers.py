"""
DRF Serializers for ABoro-Soft Helpdesk API
"""
from rest_framework import serializers
from apps.accounts.models import User
from apps.tickets.models import Ticket, TicketComment, Category
from apps.knowledge.models import KnowledgeArticle


class UserSerializer(serializers.ModelSerializer):
    """Serialize User model"""

    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'role', 'support_level', 'phone', 'department', 'location',
            'is_active', 'last_login', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'last_login']


class TicketCommentSerializer(serializers.ModelSerializer):
    """Serialize TicketComment model"""

    created_by_username = serializers.CharField(
        source='created_by.username',
        read_only=True
    )

    class Meta:
        model = TicketComment
        fields = [
            'id', 'ticket', 'created_by', 'created_by_username',
            'content', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'ticket']


class TicketSerializer(serializers.ModelSerializer):
    """Serialize Ticket model"""

    created_by_username = serializers.CharField(
        source='created_by.username',
        read_only=True
    )
    assigned_to_username = serializers.CharField(
        source='assigned_to.username',
        read_only=True,
        allow_null=True
    )
    comments = TicketCommentSerializer(many=True, read_only=True)
    category_name = serializers.CharField(
        source='category.name',
        read_only=True,
        allow_null=True
    )

    class Meta:
        model = Ticket
        fields = [
            'id', 'ticket_number', 'title', 'description',
            'created_by', 'created_by_username',
            'assigned_to', 'assigned_to_username',
            'category', 'category_name',
            'status', 'priority', 'support_level',
            'comments',
            'created_at', 'updated_at', 'closed_at'
        ]
        read_only_fields = [
            'id', 'ticket_number', 'created_by',
            'created_at', 'updated_at', 'closed_at'
        ]

    def create(self, validated_data):
        """Create ticket with current user as creator"""
        request = self.context.get('request')
        validated_data['created_by'] = request.user
        return super().create(validated_data)


class CategorySerializer(serializers.ModelSerializer):
    """Serialize Category model"""

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'color', 'is_active']
        read_only_fields = ['id']


class KnowledgeArticleSerializer(serializers.ModelSerializer):
    """Serialize KnowledgeArticle model"""

    author_name = serializers.CharField(
        source='author.username',
        read_only=True
    )

    class Meta:
        model = KnowledgeArticle
        fields = [
            'id', 'title', 'content', 'keywords',
            'author', 'author_name',
            'status', 'is_public',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'author', 'created_at', 'updated_at']
