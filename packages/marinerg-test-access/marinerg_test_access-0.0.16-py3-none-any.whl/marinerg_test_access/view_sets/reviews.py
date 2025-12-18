from rest_framework import permissions, viewsets

from ichec_django_core.models import Member

from ichec_django_core.view_sets import ObjectFileDownloadView, ObjectFileUploadView

from marinerg_test_access.models import (
    FacilityTestReport,
    AccessApplicationFacilityReview,
    AccessApplicationBoardReview,
    AccessApplicationBoardDecision,
)

from marinerg_test_access.serializers import (
    FacilityTestReportSerializer,
    AccessApplicationFacilityReviewSerializer,
    AccessApplicationBoardReviewSerializer,
    AccessApplicationBoardDecisionSerializer,
)


class FacilityTestReportViewSet(viewsets.ModelViewSet):
    queryset = FacilityTestReport.objects.all().order_by("id")
    serializer_class = FacilityTestReportSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        permissions.DjangoModelPermissions,
    ]

    def perform_create(self, serializer):
        serializer.save(creator=Member.objects.get(id=self.request.user.id))


class TestReportDownloadView(ObjectFileDownloadView):
    model = FacilityTestReport
    file_field = "report"


class TestReportUploadView(ObjectFileUploadView):
    model = FacilityTestReport
    queryset = FacilityTestReport.objects.all()
    file_field = "report"
    permission_classes = [
        permissions.IsAuthenticated,
        permissions.DjangoModelPermissions,
    ]


class AccessApplicationFacilityReviewViewSet(viewsets.ModelViewSet):
    queryset = AccessApplicationFacilityReview.objects.all().order_by("id")
    serializer_class = AccessApplicationFacilityReviewSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        permissions.DjangoModelPermissions,
    ]


class AccessApplicationBoardReviewViewSet(viewsets.ModelViewSet):
    queryset = AccessApplicationBoardReview.objects.all().order_by("id")
    serializer_class = AccessApplicationBoardReviewSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        permissions.DjangoModelPermissions,
    ]

    def perform_create(self, serializer):
        serializer.save(reviewer=Member.objects.get(id=self.request.user.id))


class AccessApplicationBoardDecisionViewSet(viewsets.ModelViewSet):
    queryset = AccessApplicationBoardDecision.objects.all().order_by("id")
    serializer_class = AccessApplicationBoardDecisionSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        permissions.DjangoModelPermissions,
    ]

    def perform_create(self, serializer):
        serializer.save(reviewer=Member.objects.get(id=self.request.user.id))
