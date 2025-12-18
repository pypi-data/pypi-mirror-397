from rest_framework import permissions

from .files import ObjectFileDownloadView, ObjectFileUploadView

from ..models import FormField, FormFieldValue


class FormFieldTemplateDownloadView(ObjectFileDownloadView):
    model = FormField
    file_field = "template"
    permissions_class = permissions.DjangoModelPermissions


class FormFieldTemplateUploadView(ObjectFileUploadView):
    model = FormField
    queryset = FormField.objects.all()
    file_field = "template"
    permission_classes = [
        permissions.IsAuthenticated,
        permissions.DjangoModelPermissions,
    ]


class FormFieldValueAssetDownloadView(ObjectFileDownloadView):
    model = FormFieldValue
    file_field = "asset"
    permissions_class = permissions.DjangoModelPermissions


class FormFieldValueAssetUploadView(ObjectFileUploadView):
    model = FormFieldValue
    queryset = FormFieldValue.objects.all()
    file_field = "asset"
    permission_classes = [
        permissions.IsAuthenticated,
        permissions.DjangoModelPermissions,
    ]
