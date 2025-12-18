try:
    from faker import Faker
    from faker_file.providers.image.pil_generator import PilImageGenerator
    from faker_file.providers.png_file import GraphicPngFileProvider

    _FAKER: Faker | None = Faker()
    if _FAKER:
        _FAKER.add_provider(GraphicPngFileProvider)
except ImportError:
    _FAKER = None

from .models import (  # NOQA
    ModelWithFiles,
    MemberCreate,
    MemberDetail,
    MemberIdentifierCreate,
    AddressCreate,
    OrganizationCreate,
    GroupCreate,
    FileWrapper,
)


def create_members(count: int = 100, offset: int = 0) -> list[ModelWithFiles]:

    content = []
    for idx in range(offset, count + offset):

        if _FAKER:
            profile = _FAKER.simple_profile()
            model = MemberCreate(
                username=str(profile["username"]),
                email=_FAKER.safe_email(),
                first_name=str(profile["name"]).split(" ")[0],
                last_name=str(profile["name"]).split(" ")[1],
                identifiers=[
                    MemberIdentifierCreate(id_type="ORCID", value="1234-5678-1234-5678")
                ],
            )
            image = _FAKER.graphic_png_file(
                image_generator_cls=PilImageGenerator, raw=True
            )
            profile_file = FileWrapper(filename=image.data["filename"], content=image)
            with open("test.png", "wb") as f:
                f.write(image)
            content.append(ModelWithFiles(model=model, files={"profile": profile_file}))
        else:
            model = MemberCreate(
                username=f"member_{idx}",
                email=f"member_{idx}@example.com",
                first_name="Script",
                last_name=f"User {idx}",
                identifiers=[
                    MemberIdentifierCreate(id_type="ORCID", value="1234-5678-1234-5678")
                ],
            )
            content.append(ModelWithFiles(model=model))
    return content


def create_groups(count: int = 100, offset: int = 0) -> list[GroupCreate]:
    content = []

    for idx in range(offset, count + offset):
        content.append(GroupCreate(name=f"Script Group {idx}"))
    return content


def create_organizations(
    count: int = 100, offset: int = 0, possible_members: tuple[MemberDetail, ...] = ()
) -> list[OrganizationCreate]:
    content = []

    for idx in range(offset, count + offset):

        if _FAKER:
            address = AddressCreate(
                line1=f"Building {_FAKER.building_number()}",
                line2=_FAKER.street_address(),
                city=_FAKER.city(),
                region="Region",
                postcode=str(_FAKER.postcode()),
                country=_FAKER.country_code(),
            )
        else:
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

        if _FAKER:
            item = OrganizationCreate(
                name=_FAKER.company(),
                acronym=f"ORG {idx}",
                description=_FAKER.paragraph(nb_sentences=5),
                address=address,
                website=_FAKER.safe_domain_name(),
                members=members,
            )
        else:
            item = OrganizationCreate(
                name=f"Organization {idx}",
                acronym=f"ORG {idx}",
                description=f"Description of org {idx}",
                address=address,
                website=f"www.org{idx}.com",
                members=members,
            )

        content.append(item)
    return content
