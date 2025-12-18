import functools

from django.db import models

from ichec_django_core.models import Organization
from ichec_django_core.models.utils import generate_thumbnail, content_file_name


class FacilityTag(models.Model):

    value = models.CharField(max_length=200)


class Facility(Organization):

    is_active = models.BooleanField(default=True)
    is_partner = models.BooleanField(default=False)
    image = models.ImageField(
        null=True, upload_to=functools.partial(content_file_name, "image")
    )
    thumbnail = models.ImageField(null=True)
    tags = models.ManyToManyField(FacilityTag, blank=True, related_name="facilities")

    class Meta:
        verbose_name = "Facility"
        verbose_name_plural = "Facilities"

    def save(self, *args, **kwargs):
        if not self.image:
            self.thumbnail = None
        else:
            try:
                self.thumbnail.name = generate_thumbnail(self, "image", self.image)
            except:  # NOQA
                self.thumbnail = None
        super().save(*args, **kwargs)


FACILITY_ID_CHOICES = [("DOI", "DOI"), ("FREEFORM", "Freeform")]


class FacilityIdentifier(models.Model):
    id_type = models.CharField(max_length=8, choices=FACILITY_ID_CHOICES)
    value = models.CharField(max_length=48)
    facility = models.ForeignKey(
        Facility, on_delete=models.CASCADE, related_name="identifiers"
    )
