from django.urls import path, include


urlpatterns = [
    path('', include('api.routes.urls')),
]

try:
    from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

    urlpatterns += [
        path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
        path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='docs'),
    ]
except ImportError:
    pass

try:
    from drf_yasg import openapi
    from drf_yasg.views import get_schema_view
    from rest_framework import permissions

    schema_view = get_schema_view(
        openapi.Info(
            title="API Companias y Empleados",
            default_version='v1',
            description="API REST con Django y Onion Architecture",
        ),
        public=True,
        permission_classes=[permissions.AllowAny],
    )

    urlpatterns += [
        path('swagger/', schema_view.with_ui('swagger', cache_timeout=0)),
        path('redoc/', schema_view.with_ui('redoc', cache_timeout=0)),
    ]
except ImportError:
    pass
