from django.urls import include, path
from django.contrib import admin
from django.conf import settings

from .view_sets import (
    MemberViewSet,
    MemberSelfView,
    MemberProfileDownloadView,
    MemberProfileThumbnailDownloadView,
    MemberProfileUploadView,
    GroupViewSet,
    OrganizationViewSet,
    FeedbackViewSet,
    AddressViewSet,
    CustomAuthToken,
    GetAuthToken,
    FormFieldTemplateDownloadView,
    FormFieldTemplateUploadView,
    FormFieldValueAssetDownloadView,
    FormFieldValueAssetUploadView,
)
from .view_sets.core import server_manifest


def register_drf_views(router):
    router.register(r"groups", GroupViewSet)
    router.register(r"organizations", OrganizationViewSet)
    router.register(r"members", MemberViewSet)
    router.register(r"addresses", AddressViewSet)
    router.register(r"feedback", FeedbackViewSet)
    return router


urlpatterns = [
    path("api-token-auth/", CustomAuthToken.as_view()),
    path(f"{settings.API_AUTH_URL}/", include("rest_framework.urls")),
    path(f"{settings.ADMIN_URL}/", admin.site.urls),
    path(
        r"manifest",
        server_manifest,
        name="manifest",
    ),
    path(
        r"api/self/",
        MemberSelfView.as_view(),
        name="member_self",
    ),
    path(
        r"api/token/",
        GetAuthToken.as_view(),
        name="token",
    ),
    path(
        r"api/members/<int:pk>/profile",
        MemberProfileDownloadView.as_view(),
        name="member_profiles",
    ),
    path(
        r"api/members/<int:pk>/profile/thumbnail",
        MemberProfileThumbnailDownloadView.as_view(),
        name="member_profile_thumbnails",
    ),
    path(
        r"api/members/<int:pk>/profile/upload",
        MemberProfileUploadView.as_view(),
        name="member_profiles_upload",
    ),
    path(
        r"api/form_fields/<int:pk>/template",
        FormFieldTemplateDownloadView.as_view(),
        name="form_field_templates",
    ),
    path(
        r"api/form_fields/<int:pk>/template/upload",
        FormFieldTemplateUploadView.as_view(),
        name="form_field_templates_upload",
    ),
    path(
        r"api/form_field_values/<int:pk>/asset",
        FormFieldValueAssetDownloadView.as_view(),
        name="form_field_value_assets",
    ),
    path(
        r"api/form_field_values/<int:pk>/asset/upload",
        FormFieldValueAssetUploadView.as_view(),
        name="form_field_value_assets_upload",
    ),
    path("", include("django_prometheus.urls")),
]

if settings.WITH_OIDC:
    urlpatterns += [path("oidc/", include("mozilla_django_oidc.urls"))]
