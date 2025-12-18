import functools

from django.db import models

from ichec_django_core.models import Member, TimesStampMixin, content_file_name

from marinerg_data_access.models import Dataset
from marinerg_facility.models import Facility

from .application import AccessApplication


class FacilityTestReport(TimesStampMixin):

    creator = models.ForeignKey(Member, on_delete=models.CASCADE)
    report = models.FileField(
        null=True, upload_to=functools.partial(content_file_name, "report")
    )

    datasets = models.ManyToManyField(
        Dataset,
        verbose_name="Datasets",
        related_name="test_reports",
        blank=True,
    )

    confirmed_complies_data_mgmt = models.BooleanField(default=False)
    application = models.ForeignKey(AccessApplication, on_delete=models.CASCADE)
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE, null=True)


class AccessApplicationFacilityReview(TimesStampMixin):

    confirmed_preapplication_discussion = models.BooleanField(default=False)
    confirmed_app_info_in_line_with_discussion = models.BooleanField(default=False)
    supporting_comments = models.TextField(blank=True)
    supporting_documents = models.FileField(null=True)
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE)
    application = models.ForeignKey(AccessApplication, on_delete=models.CASCADE)


class AccessApplicationBoardReview(TimesStampMixin):
    class Decision(models.TextChoices):
        ACCEPT = "1", "ACCEPT"
        REJECT = "2", "REJECT"

    decision = models.CharField(max_length=10, choices=Decision.choices)
    comments = models.TextField(blank=True)
    application = models.ForeignKey(
        AccessApplication, on_delete=models.CASCADE, null=True
    )
    reviewer = models.ForeignKey(Member, on_delete=models.CASCADE)

    def save(self, force_insert=False, force_update=False, *args, **kwargs):

        self.application.status = "DECISION"
        self.application.save()

        super().save(force_insert, force_update, *args, **kwargs)


class AccessApplicationBoardDecision(TimesStampMixin):
    class Decision(models.TextChoices):
        ACCEPT = "1", "ACCEPT"
        REJECT = "2", "REJECT"

    decision = models.CharField(max_length=10, choices=Decision.choices)
    comments = models.TextField(blank=True)
    application = models.ForeignKey(
        AccessApplication, on_delete=models.CASCADE, null=True
    )
    reviewer = models.ForeignKey(Member, on_delete=models.CASCADE)

    def save(self, force_insert=False, force_update=False, *args, **kwargs):

        if self.decision == "1":
            self.application.status = "ACCEPTED"
        else:
            self.application.status = "REJECTED"
        self.application.save()

        super().save(force_insert, force_update, *args, **kwargs)
