"""
REST API Views for ABoro-Soft Helpdesk
Provides complete API access for Desktop clients and third-party integrations
"""
from django.contrib.auth import authenticate
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Q
import json
import logging

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from apps.accounts.models import User
from apps.tickets.models import Ticket, TicketComment, Category
from apps.knowledge.models import KnowledgeArticle
from .serializers import (
    UserSerializer, TicketSerializer, TicketCommentSerializer,
    CategorySerializer, KnowledgeArticleSerializer
)
from .license_manager import LicenseManager

logger = logging.getLogger(__name__)


class LicenseValidationMixin:
    """Mixin to validate license for API calls"""

    def validate_license(self, request):
        """Validate license key from request headers"""
        license_key = request.META.get('HTTP_X_LICENSE_KEY')
        if not license_key:
            return False, Response(
                {'error': 'License key required', 'code': 'NO_LICENSE'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        is_valid, error = LicenseManager.validate_license(license_key)
        if not is_valid:
            return False, Response(
                {'error': error, 'code': 'INVALID_LICENSE'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        return True, None


class AuthViewSet(viewsets.ViewSet):
    """Authentication endpoints"""

    @csrf_exempt
    @require_http_methods(["POST"])
    def login(self, request):
        """
        Login and get API token
        POST /api/v1/auth/login/
        Body: {"email": "...", "password": "..."}
        """
        try:
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')

            user = authenticate(username=email, password=password)
            if user is None:
                return Response(
                    {'error': 'Invalid credentials'},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            # Generate or get token
            from rest_framework.authtoken.models import Token
            token, created = Token.objects.get_or_create(user=user)

            return Response({
                'token': token.key,
                'user': UserSerializer(user).data,
                'success': True
            })
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @csrf_exempt
    @require_http_methods(["POST"])
    def logout(self, request):
        """Logout and invalidate token"""
        try:
            from rest_framework.authtoken.models import Token
            Token.objects.filter(user=request.user).delete()
            return Response({'success': True, 'message': 'Logged out'})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @csrf_exempt
    @require_http_methods(["POST"])
    def validate_license(self, request):
        """
        Validate license key
        POST /api/v1/auth/validate-license/
        Headers: X-License-Key: <key>
        """
        license_key = request.META.get('HTTP_X_LICENSE_KEY')
        if not license_key:
            return Response(
                {'error': 'License key required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        is_valid, error = LicenseManager.validate_license(license_key)
        if is_valid:
            info = LicenseManager.get_license_info(license_key)
            return Response({
                'valid': True,
                'license_info': info
            })
        else:
            return Response(
                {'error': error, 'valid': False},
                status=status.HTTP_401_UNAUTHORIZED
            )


class TicketViewSet(viewsets.ModelViewSet, LicenseValidationMixin):
    """Ticket management API endpoints"""

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = TicketSerializer

    def get_queryset(self):
        """Filter tickets based on user role"""
        user = self.request.user

        if user.role == 'admin':
            return Ticket.objects.all()
        elif user.role == 'support_agent':
            return Ticket.objects.filter(
                Q(assigned_to=user) | Q(assigned_to__isnull=True)
            )
        else:  # customer
            return Ticket.objects.filter(created_by=user)

    def list(self, request, *args, **kwargs):
        """
        List tickets
        GET /api/v1/tickets/
        Query params: ?status=open&priority=high&page=1
        """
        is_valid, error_response = self.validate_license(request)
        if not is_valid:
            return error_response

        queryset = self.get_queryset()

        # Filter by status
        status_filter = request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        # Filter by priority
        priority = request.query_params.get('priority')
        if priority:
            queryset = queryset.filter(priority=priority)

        # Filter by assigned_to
        assigned_to = request.query_params.get('assigned_to')
        if assigned_to and request.user.role == 'admin':
            queryset = queryset.filter(assigned_to_id=assigned_to)

        # Pagination
        page = request.query_params.get('page', 1)
        paginator = Paginator(queryset, 20)
        page_obj = paginator.get_page(page)

        serializer = self.serializer_class(page_obj.object_list, many=True)
        return Response({
            'tickets': serializer.data,
            'total': paginator.count,
            'pages': paginator.num_pages,
            'current_page': page_obj.number
        })

    def retrieve(self, request, pk=None):
        """
        Get single ticket
        GET /api/v1/tickets/{id}/
        """
        is_valid, error_response = self.validate_license(request)
        if not is_valid:
            return error_response

        try:
            ticket = self.get_queryset().get(pk=pk)
            serializer = self.serializer_class(ticket)
            return Response(serializer.data)
        except Ticket.DoesNotExist:
            return Response(
                {'error': 'Ticket not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    def create(self, request):
        """
        Create new ticket
        POST /api/v1/tickets/
        Body: {"title": "...", "description": "...", "priority": "high", ...}
        """
        is_valid, error_response = self.validate_license(request)
        if not is_valid:
            return error_response

        try:
            serializer = self.serializer_class(
                data=request.data,
                context={'request': request}
            )
            if serializer.is_valid():
                serializer.save(created_by=request.user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Create ticket error: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def update(self, request, pk=None):
        """
        Update ticket
        PUT/PATCH /api/v1/tickets/{id}/
        """
        is_valid, error_response = self.validate_license(request)
        if not is_valid:
            return error_response

        try:
            ticket = self.get_queryset().get(pk=pk)

            # Check permissions
            if request.user.role == 'customer' and ticket.created_by != request.user:
                return Response(
                    {'error': 'Permission denied'},
                    status=status.HTTP_403_FORBIDDEN
                )

            serializer = self.serializer_class(
                ticket,
                data=request.data,
                partial=True,
                context={'request': request}
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Ticket.DoesNotExist:
            return Response(
                {'error': 'Ticket not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def add_comment(self, request, pk=None):
        """
        Add comment to ticket
        POST /api/v1/tickets/{id}/add_comment/
        Body: {"content": "..."}
        """
        is_valid, error_response = self.validate_license(request)
        if not is_valid:
            return error_response

        try:
            ticket = self.get_queryset().get(pk=pk)
            content = request.data.get('content')

            if not content:
                return Response(
                    {'error': 'Content required'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            comment = TicketComment.objects.create(
                ticket=ticket,
                created_by=request.user,
                content=content
            )

            serializer = TicketCommentSerializer(comment)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Ticket.DoesNotExist:
            return Response(
                {'error': 'Ticket not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        """
        Assign ticket to agent
        POST /api/v1/tickets/{id}/assign/
        Body: {"assigned_to": user_id}
        """
        if request.user.role != 'admin' and request.user.role != 'support_agent':
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            ticket = Ticket.objects.get(pk=pk)
            assigned_to_id = request.data.get('assigned_to')

            if assigned_to_id:
                assigned_to = User.objects.get(id=assigned_to_id)
                ticket.assigned_to = assigned_to
            else:
                ticket.assigned_to = None

            ticket.save()
            serializer = self.serializer_class(ticket)
            return Response(serializer.data)
        except (Ticket.DoesNotExist, User.DoesNotExist):
            return Response(
                {'error': 'Resource not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=['post'])
    def change_status(self, request, pk=None):
        """
        Change ticket status
        POST /api/v1/tickets/{id}/change_status/
        Body: {"status": "resolved"}
        """
        try:
            ticket = self.get_queryset().get(pk=pk)
            new_status = request.data.get('status')

            if new_status not in dict(Ticket.STATUS_CHOICES):
                return Response(
                    {'error': 'Invalid status'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            ticket.status = new_status
            ticket.save()

            serializer = self.serializer_class(ticket)
            return Response(serializer.data)
        except Ticket.DoesNotExist:
            return Response(
                {'error': 'Ticket not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class CategoryViewSet(viewsets.ModelViewSet, LicenseValidationMixin):
    """Category management API"""

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def list(self, request):
        """GET /api/v1/categories/"""
        is_valid, error_response = self.validate_license(request)
        if not is_valid:
            return error_response

        serializer = self.serializer_class(self.queryset, many=True)
        return Response(serializer.data)


class StatsViewSet(viewsets.ViewSet, LicenseValidationMixin):
    """Statistics API endpoints"""

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """
        Get dashboard statistics
        GET /api/v1/stats/
        """
        is_valid, error_response = self.validate_license(request)
        if not is_valid:
            return error_response

        stats = request.user.get_dashboard_stats()
        return Response(stats)

    @action(detail=False, methods=['get'])
    def performance(self, request):
        """
        Get team performance metrics
        GET /api/v1/stats/performance/
        """
        if request.user.role != 'admin' and request.user.role != 'support_agent':
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Get all tickets
        tickets = Ticket.objects.all()

        stats = {
            'total_tickets': tickets.count(),
            'open_tickets': tickets.filter(status='open').count(),
            'in_progress': tickets.filter(status='in_progress').count(),
            'resolved': tickets.filter(status='resolved').count(),
            'closed': tickets.filter(status='closed').count(),
            'average_resolution_time': None,  # Calculate if needed
        }

        return Response(stats)

    @action(detail=False, methods=['get'])
    def by_agent(self, request):
        """
        Get statistics by support agent
        GET /api/v1/stats/by_agent/
        """
        if request.user.role != 'admin':
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )

        agents = User.objects.filter(role='support_agent')
        stats = {}

        for agent in agents:
            agent_tickets = Ticket.objects.filter(assigned_to=agent)
            stats[agent.username] = {
                'total': agent_tickets.count(),
                'open': agent_tickets.filter(status='open').count(),
                'resolved': agent_tickets.filter(status='resolved').count(),
                'closed': agent_tickets.filter(status='closed').count(),
            }

        return Response(stats)


class HealthCheckViewSet(viewsets.ViewSet):
    """Health check endpoints"""

    @csrf_exempt
    @require_http_methods(["GET"])
    def check(self, request):
        """
        Health check endpoint
        GET /api/v1/health/
        """
        return Response({
            'status': 'healthy',
            'version': '1.0.0',
            'timestamp': str(timezone.now())
        })


# NOTE: License generation endpoint is intentionally NOT included in the customer-facing API
# License codes must be generated through a separate, internal-only tool to prevent customers
# from generating their own licenses, which would destroy the sales model.
#
# See: tools/license_generator_internal.py (for internal use only)
