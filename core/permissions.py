from rest_framework import permissions
from django.conf import settings

class HasValidAPIKey(permissions.BasePermission):
    
    def has_permission(self, request, view):  # ← Corregido aquí
        api_key = request.headers.get("API-Key")
        return api_key in getattr(settings, "VALID_API_KEYS", [])
