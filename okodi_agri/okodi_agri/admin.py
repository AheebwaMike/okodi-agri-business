# okodi_agri/okodi_agri/admin.py

from django.contrib import admin
from django.contrib.admin import AdminSite
from django.utils.translation import gettext_lazy as _

class OkodiAdminSite(AdminSite):
    site_header = _('Okodi Agri-Business Administration')
    site_title = _('Okodi Agri CMS')
    index_title = _('Dashboard')
    
    def get_app_list(self, request):
        app_list = super().get_app_list(request)
        # Custom ordering of apps
        app_list = sorted(app_list, key=lambda x: x['name'])
        return app_list

# Unregister default admin site and use custom one
admin_site = OkodiAdminSite(name='myadmin')