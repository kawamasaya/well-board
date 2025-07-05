"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from backend.urls import router, tenant_router
from backend.views import (
    registration_view,
    token_delete_view,
    token_obtain_view,
    token_refresh_view,
    token_verify_view,
)

api_urlpatterns = [
    path('auth/', token_obtain_view.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/verify/', token_verify_view.CustomTokenVerifyView.as_view(), name='token_verify'),
    path('auth/refresh/', token_refresh_view.CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('auth/logout/', token_delete_view.TokenDeleteView.as_view(), name='token_refresh'),
    path('auth/tenant-request/', registration_view.TenantRequestView.as_view(), name='tenant_request'),
    path('', include(router.urls)),
    path('', include(tenant_router.urls)),
]

urlpatterns = [
    path('api/', include(api_urlpatterns)),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('admin/', admin.site.urls),
    path('', include('backend.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
