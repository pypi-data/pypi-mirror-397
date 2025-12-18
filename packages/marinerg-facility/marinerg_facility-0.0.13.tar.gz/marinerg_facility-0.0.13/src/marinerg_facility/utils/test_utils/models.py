from pydantic import BaseModel

from ichec_django_core.utils.test_utils.models import (
    Timestamped,
    Resource,
    Identifiable,
    register_types,
    AddressCreate,
    AddressDetail,
)


class FacilityTagBase(BaseModel, frozen=True):
    value: str


class FacilityTagCreate(FacilityTagBase, frozen=True):
    pass


class FacilityTagDetail(Identifiable, FacilityTagBase, frozen=True):
    pass


class FacillityIdentifierBase(BaseModel, frozen=True):
    id_type: str
    value: str


class FacilityIdentifierCreate(FacilityTagBase, frozen=True):
    pass


class FacilityIdentifierDetail(FacillityIdentifierBase, Resource, frozen=True):
    pass


class FacilityBase(BaseModel, frozen=True):
    name: str
    acronym: str | None = None
    description: str | None = None
    website: str | None = None
    profile: str = ""
    members: list[str] = []
    tags: list[str] = []


class FacilityCreate(FacilityBase, frozen=True):
    address: AddressCreate
    identifiers: list[FacilityIdentifierCreate] = []


class FacilityDetail(Timestamped, FacilityBase, frozen=True):
    address: AddressDetail
    identifiers: list[FacilityIdentifierDetail] = []


class EquipmentBase(BaseModel, frozen=True):
    name: str
    description: str | None = None
    image: str | None = None
    facility: str


class EquipmentCreate(EquipmentBase, frozen=True):
    pass


class EquipmentDetail(Timestamped, EquipmentBase, frozen=True):
    thumbnail: str | None


register_types("facilities", {"create": FacilityCreate, "detail": FacilityDetail})
register_types("equipment", {"create": EquipmentCreate, "detail": EquipmentDetail})
