import functools

from django.db import models

from ichec_django_core.models.utils import (
    generate_thumbnail,
    content_file_name,
    TimesStampMixin,
)

from .facility import Facility


class EquipmentTag(models.Model):

    value = models.CharField(max_length=200)


class Equipment(TimesStampMixin):

    name = models.CharField(max_length=500)
    description = models.CharField()
    facility = models.ForeignKey(
        Facility, on_delete=models.CASCADE, related_name="equipment"
    )

    image = models.ImageField(
        null=True, upload_to=functools.partial(content_file_name, "image")
    )
    thumbnail = models.ImageField(null=True)
    tags = models.ManyToManyField(EquipmentTag, blank=True, related_name="equipment")

    def save(self, *args, **kwargs):
        if not self.image:
            self.thumbnail = None
        else:
            self.thumbnail.name = generate_thumbnail(self, "image", self.image)
        super().save(*args, **kwargs)
