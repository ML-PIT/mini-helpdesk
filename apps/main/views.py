from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin


@login_required
def dashboard(request):
    """Main dashboard view"""
    context = {
        'stats': request.user.get_dashboard_stats() if hasattr(request.user, 'get_dashboard_stats') else {}
    }
    return render(request, 'dashboard/index.html', context)


class DashboardView(LoginRequiredMixin, TemplateView):
    """Dashboard class-based view"""
    template_name = 'dashboard/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['stats'] = self.request.user.get_dashboard_stats()
        return context
