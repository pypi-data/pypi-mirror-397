from pathlib import Path

from pydantic import BaseModel

from ichec_django_core.utils.test_utils.models import (
    AddressCreate,
    MemberDetail,
    ModelWithFiles,
    FileWrapper,
)

from .models import FacilityCreate, FacilityDetail, EquipmentCreate


class ContentEquipment(BaseModel):
    title: str | None
    attributes: list[str] = []


class ContentFacility(BaseModel, frozen=True):

    name: str
    acronym: str
    description: str
    address: str
    website: str
    country: str
    figure: str
    equipment: list[ContentEquipment]
    members: list[str] = []


_COUNTRIES = [
    ("United Kingdom", "UK"),
    ("Spain", "ES"),
    ("France", "FR"),
    ("Germany", "DE"),
    ("Italy", "IE"),
    ("Netherlands", "NL"),
    ("Cyprus", "CY"),
    ("Denmark", "CK"),
    ("Greece", "GR"),
    ("Portugal", "PT"),
]


def get_country_code(country: str) -> str:
    for c in _COUNTRIES:
        if c[0] == country:
            return c[1]
    raise RuntimeError("Country not found")


def parse_address(content: str) -> AddressCreate:
    lines = content.splitlines()

    line1 = lines[0]
    country_code = None
    region = None
    postcode = ""
    for country in _COUNTRIES:
        if country[0] in lines[-1]:
            country_code = country[1]
            last_no_country = lines[-1].replace(country[0], "").split(" ")
            if len(last_no_country) >= 2:
                region = last_no_country[1]
                postcode = last_no_country[0]
        else:
            country_code = "IE"
            pc_region = lines[-1].split(" ")
            if len(pc_region) >= 2:
                region = pc_region[1]
                postcode = pc_region[0]

    return AddressCreate(
        line1=line1, region=region, postcode=postcode, country=country_code
    )


def content_to_facility(
    content: ContentFacility,
    idx,
    possible_members: tuple[MemberDetail, ...],
    image_path: Path,
) -> tuple[ModelWithFiles, list[ContentEquipment]]:

    members = []
    if possible_members:
        num_members = len(possible_members) - 1
        ids = set(
            [
                idx % num_members,
                (idx + 1) % num_members,
                (idx + 2) % num_members,
                (idx + 4) % num_members,
            ]
        )
        members = [possible_members[jdx].url for jdx in ids]

    image_full_path = image_path / Path(content.figure).name
    with open(image_full_path, "rb") as f:
        image_data = f.read()

    image = FileWrapper(filename=str(image_full_path), content=image_data)

    return (
        ModelWithFiles(
            model=FacilityCreate(
                name=content.name,
                acronym=content.acronym,
                description=content.description,
                website=content.website,
                address=parse_address(content.address),
                members=members,
                identifiers=[],
                tags=[],
            ),
            files={"image": image},
        ),
        content.equipment,
    )


def create_equipment(
    facilities: list[FacilityDetail], equipment: list[list[ContentEquipment]]
) -> list[EquipmentCreate]:

    ret = []
    for facility, facility_equipment in zip(facilities, equipment):
        for e in facility_equipment:
            if e.title:
                if e.attributes:
                    description = "Attributes\n" + "\n".join(a for a in e.attributes)
                else:
                    description = "No Description"
                ret.append(
                    EquipmentCreate(
                        facility=facility.url,
                        name=e.title,
                        description=description,
                    )
                )
    return ret


def load_facilities(
    content: dict, members: tuple[MemberDetail, ...], image_path: Path
) -> list:
    facilities = [ContentFacility(**f) for f in content]
    return [
        content_to_facility(f, idx, members, image_path)
        for idx, f in enumerate(facilities)
    ]


def create_facilities(
    count=100, offset: int = 0, possible_members: tuple[MemberDetail, ...] = ()
) -> list[FacilityCreate]:

    content = []

    for idx in range(offset, count + offset):
        address = AddressCreate(
            line1="Apartment 123",
            line2="123 Street",
            city="City",
            region="Region",
            postcode="abc123",
            country="IE",
        )

        members = []
        if possible_members:
            num_members = len(possible_members) - 1
            ids = set(
                [
                    idx % num_members,
                    (idx + 1) % num_members,
                    (idx + 2) % num_members,
                    (idx + 4) % num_members,
                ]
            )
            members = [possible_members[jdx].url for jdx in ids]

        item = FacilityCreate(
            name=f"Facility {idx}",
            acronym=f"FAC {idx}",
            description=f"Description of facility {idx}",
            address=address,
            website=f"www.faciliy{idx}.com",
            members=members,
            identifiers=[],
            tags=[],
        )

        content.append(item)

    return content
