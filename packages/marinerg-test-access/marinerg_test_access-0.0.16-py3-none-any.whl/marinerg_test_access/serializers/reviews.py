from rest_framework import serializers

from marinerg_test_access.models import (
    FacilityTestReport,
    AccessApplicationFacilityReview,
    AccessApplicationBoardReview,
    AccessApplicationBoardDecision,
)


class FacilityTestReportSerializer(serializers.HyperlinkedModelSerializer):

    report = serializers.HyperlinkedIdentityField(
        read_only=True, view_name="test_reports"
    )

    class Meta:
        model = FacilityTestReport
        fields = [
            "creator",
            "report",
            "datasets",
            "confirmed_complies_data_mgmt",
            "application",
            "facility",
            "id",
            "url",
        ]
        read_only_fields = ("creator", "report", "id", "url")

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        if not instance.report:
            rep["report"] = None
        return rep


class AccessApplicationFacilityReviewSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = AccessApplicationFacilityReview
        fields = [
            "confirmed_preapplication_discussion",
            "confirmed_app_info_in_line_with_discussion",
            "supporting_comments",
            "supporting_documents",
            "application",
            "facility",
        ]


class AccessApplicationBoardReviewSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = AccessApplicationBoardReview
        fields = ["decision", "comments", "reviewer", "application"]
        read_only_fields = ("reviewer",)


class AccessApplicationBoardDecisionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = AccessApplicationBoardDecision
        fields = ["decision", "comments", "reviewer", "application"]
        read_only_fields = ("reviewer",)
