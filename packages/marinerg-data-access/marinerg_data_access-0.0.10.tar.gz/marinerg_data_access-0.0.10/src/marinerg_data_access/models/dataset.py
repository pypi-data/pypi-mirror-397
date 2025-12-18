from django.db import models

from ichec_django_core.models import Member, PopulatedForm, TimesStampMixin

from marinerg_facility.models import Facility, Equipment

from .dataset_template import DatasetTemplate


class DatasetTag(models.Model):

    value = models.CharField(max_length=200)


class Dataset(TimesStampMixin):

    creator = models.ForeignKey(Member, on_delete=models.CASCADE)

    title = models.CharField(max_length=250)

    description = models.TextField(blank=True)

    uri = models.CharField(max_length=250, null=True)

    id_authority = models.CharField(max_length=250, null=True)

    tags = models.ManyToManyField(DatasetTag, blank=True, related_name="datasets")

    license = models.CharField(max_length=250, null=True)

    parent = models.ForeignKey(
        "self", null=True, blank=True, related_name="children", on_delete=models.CASCADE
    )

    is_public = models.BooleanField(default=True)

    access_instructions = models.TextField(blank=True, null=True)

    equipment = models.ForeignKey(
        Equipment, null=True, related_name="datasets", on_delete=models.SET_NULL
    )

    facility = models.ForeignKey(
        Facility, null=True, related_name="datasets", on_delete=models.SET_NULL
    )

    template = models.ForeignKey(
        DatasetTemplate, null=True, related_name="datasets", on_delete=models.SET_NULL
    )

    form = models.OneToOneField(PopulatedForm, null=True, on_delete=models.CASCADE)
