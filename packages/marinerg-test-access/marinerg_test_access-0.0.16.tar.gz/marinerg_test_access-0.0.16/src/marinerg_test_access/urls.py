from django.urls import path

from .view_sets import (
    AccessApplicationViewSet,
    SummaryDownloadView,
    AccessCallViewSet,
    ApplicationSummaryDownloadView,
    AccessCallFacilityReviewViewSet,
    AccessApplicationFacilityReviewViewSet,
    AccessApplicationBoardReviewViewSet,
    AccessApplicationBoardDecisionViewSet,
    FacilityTestReportViewSet,
    TestReportDownloadView,
    TestReportUploadView,
)


def register_drf_views(router):
    router.register(r"access_calls", AccessCallViewSet)
    router.register(r"access_call_facility_reviews", AccessCallFacilityReviewViewSet)
    router.register(r"access_applications", AccessApplicationViewSet)
    router.register(
        r"access_application_facility_reviews", AccessApplicationFacilityReviewViewSet
    )
    router.register(
        r"access_application_board_reviews", AccessApplicationBoardReviewViewSet
    )
    router.register(
        r"access_application_board_decisions", AccessApplicationBoardDecisionViewSet
    )
    router.register(r"facility_test_reports", FacilityTestReportViewSet)


urlpatterns = [
    path(
        r"access_calls/<int:pk>/application_summary",
        ApplicationSummaryDownloadView.as_view(),
        name="call_application_summaries",
    ),
    path(
        r"access_applications/<int:pk>/summary",
        SummaryDownloadView.as_view(),
        name="application_summaries",
    ),
    path(
        r"facility_test_reports/<int:pk>/report",
        TestReportDownloadView.as_view(),
        name="test_reports",
    ),
    path(
        r"facility_test_reports/<int:pk>/report/upload",
        TestReportUploadView.as_view(),
        name="test_report_uploads",
    ),
]
