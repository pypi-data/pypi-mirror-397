from rest_framework import serializers

from marinerg_facility.models import Facility, FacilityIdentifier, FacilityTag

from ichec_django_core.models import Address
from ichec_django_core.serializers import (
    AddressSerializer,
    NestedHyperlinkedModelSerializer,
)


class FacilityIdentifierSerializer(serializers.ModelSerializer):

    # Needs explicit inclusion to use in Member list serializer updates
    id = serializers.IntegerField(required=False)

    class Meta:
        model = FacilityIdentifier
        fields = ("id", "id_type", "value")


class FacilityTagSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = FacilityTag
        fields = ("value", "id", "url")
        read_only_fields = ("value", "id", "url")


class FacilityBaseSerializer(NestedHyperlinkedModelSerializer):

    address = AddressSerializer()
    identifiers = FacilityIdentifierSerializer(many=True)

    class Meta:
        model = Facility
        fields = NestedHyperlinkedModelSerializer.base_fields + (
            "name",
            "acronym",
            "description",
            "address",
            "website",
            "is_active",
            "members",
            "image",
            "thumbnail",
            "equipment",
            "identifiers",
            "tags",
        )
        read_only_fields = NestedHyperlinkedModelSerializer.base_fields + (
            "image",
            "equipment",
            "thumbnail",
        )


class FacilityResponseSerializer(FacilityBaseSerializer):

    image = serializers.HyperlinkedIdentityField(
        read_only=True, view_name="facility_images"
    )
    thumbnail = serializers.HyperlinkedIdentityField(
        read_only=True, view_name="facility_thumbnails"
    )

    class Meta:
        model = Facility
        fields = FacilityBaseSerializer.Meta.fields
        read_only_fields = FacilityBaseSerializer.Meta.read_only_fields + ("image",)

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        if not instance.image:
            rep["image"] = None
        if not instance.thumbnail:
            rep["thumbnail"] = None
        return rep


class FacilityListSerializer(FacilityBaseSerializer):

    def to_representation(self, instance):
        return FacilityResponseSerializer(context=self.context).to_representation(
            instance
        )


class FacilityDetailSerializer(FacilityBaseSerializer):

    def to_representation(self, instance):
        return FacilityResponseSerializer(context=self.context).to_representation(
            instance
        )

    def create(self, validated_data):
        address_data = validated_data.pop("address")
        address = Address.objects.create(**address_data)

        ids = validated_data.pop("identifiers")

        many_to_many = self.pop_many_to_many(validated_data)
        instance = Facility.objects.create(address=address, **validated_data)

        FacilityIdentifier.objects.bulk_create(
            [FacilityIdentifier(facility=instance, **eachId) for eachId in ids]
        )

        self.add_many_to_many(instance, many_to_many)
        return instance

    def get_existing(self, id: str, collection: list):
        for c in collection:
            if c.id == id:
                return c
        raise RuntimeError("Requested non-existing entry")

    def update(self, instance, validated_data):
        incoming_ids = validated_data.pop("identifiers")
        address_data = validated_data.pop("address")

        instance = super().update(instance, validated_data)

        for attr, value in address_data.items():
            setattr(instance.address, attr, value)
        instance.address.save()

        all_existing = instance.identifiers.all()

        # If any ids no longer exist delete them
        incoming_ids_ids = [
            incoming["id"] for incoming in incoming_ids if "id" in incoming
        ]
        existing_ids = [existing.id for existing in all_existing]
        for existing in existing_ids:
            if existing not in incoming_ids_ids:
                FacilityIdentifier.objects.get(id=existing).delete()

        # If there is an id do an update, else do a create
        serializer = FacilityIdentifierSerializer()
        for eachId in incoming_ids:
            if "id" not in eachId:
                FacilityIdentifier.objects.create(member=instance, **eachId)
            else:
                serializer.update(self.get_existing(eachId["id"], all_existing), eachId)
        return instance
