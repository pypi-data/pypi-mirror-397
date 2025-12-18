from rest_framework import serializers

from ichec_django_core.models import Member
from ichec_django_core.serializers import (
    NestedHyperlinkedModelSerializer,
    PopulatedFormSerializer,
)

from marinerg_test_access.models import AccessApplication


class AccessApplicationBaseSerializer(NestedHyperlinkedModelSerializer):

    form = PopulatedFormSerializer()

    class Meta:
        model = AccessApplication
        fields = (
            "facilities",
            "request_start_date",
            "request_end_date",
            "dates_flexible",
            "call",
            "form",
            "status",
        )


class AccessApplicationDetailSerializer(AccessApplicationBaseSerializer):

    call_title = serializers.CharField(
        source="call.title", required=False, read_only=True
    )
    applicant_username = serializers.CharField(
        source="applicant.username", required=False, read_only=True
    )

    summary = serializers.HyperlinkedIdentityField(
        read_only=True, view_name="application_summaries"
    )

    is_selectable_facility_member = serializers.SerializerMethodField()
    is_selected_facility_member = serializers.SerializerMethodField()

    def get_is_selectable_facility_member(self, obj):
        user = self.context.get("request").user

        members = Member.objects.filter(id=user.id)
        if not members:
            return False

        org_ids = [org.id for org in members.first().organizations.all()]
        selectable_ids = [f.id for f in obj.facilities.all()]
        return any(org_id in selectable_ids for org_id in org_ids)

    def get_is_selected_facility_member(self, obj):
        user = self.context.get("request").user

        if not obj.chosen_facility:
            return False

        members_ids = [m.id for m in obj.chosen_facility.members.all()]
        return user.id in members_ids

    def update(self, instance, validated_data):
        form = validated_data.pop("form")

        instance = super().update(instance, validated_data)

        serializer = PopulatedFormSerializer()
        serializer.update(instance.form, form)

        return instance

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        if not instance.summary:
            rep["summary"] = None
        return rep

    class Meta:
        model = AccessApplication
        fields = (
            tuple(AccessApplicationBaseSerializer.Meta.fields)
            + NestedHyperlinkedModelSerializer.base_fields
            + (
                "chosen_facility",
                "summary",
                "applicant",
                "call",
                "submitted",
                "call_title",
                "applicant_username",
                "is_selectable_facility_member",
                "is_selected_facility_member",
            )
        )
        read_only_fields = NestedHyperlinkedModelSerializer.base_fields + (
            "submitted",
            "applicant",
            "call_title",
            "summary",
            "applicant_username",
            "is_selectable_facility_member",
            "is_selected_facility_member",
        )


class AccessApplicationCreateSerializer(AccessApplicationBaseSerializer):

    class Meta:
        model = AccessApplication
        fields = AccessApplicationBaseSerializer.Meta.fields

    def create(self, validated_data):

        form = validated_data.pop("form")
        form_instance = PopulatedFormSerializer().create(form)

        many_to_many = self.pop_many_to_many(validated_data)
        instance = AccessApplication.objects.create(
            form=form_instance, **validated_data
        )
        self.add_many_to_many(instance, many_to_many)
        return instance

    def to_representation(self, instance):
        return AccessApplicationDetailSerializer(
            context=self.context
        ).to_representation(instance)
