from rest_framework import serializers

from ichec_django_core.models import Member, MemberIdentifier

from .core import SERIALIZER_BASE_FIELDS


class MemberIdentifierSerializer(serializers.ModelSerializer):

    # Needs explicit inclusion to use in Member list serializer updates
    id = serializers.IntegerField(required=False)

    class Meta:
        model = MemberIdentifier
        fields = ("id", "id_type", "value")


class MemberBaseSerializer(serializers.HyperlinkedModelSerializer):

    identifiers = MemberIdentifierSerializer(many=True)

    class Meta:
        model = Member
        fields = SERIALIZER_BASE_FIELDS + (
            "username",
            "email",
            "first_name",
            "last_name",
            "phone",
            "profile",
            "identifiers",
        )
        read_only_fields = SERIALIZER_BASE_FIELDS + ("profile",)

    def create(self, validated_data):
        ids = validated_data.pop("identifiers")

        instance = super().create(validated_data)
        MemberIdentifier.objects.bulk_create(
            [MemberIdentifier(member=instance, **eachId) for eachId in ids]
        )
        return instance

    def get_existing(self, id: str, collection: list):
        for c in collection:
            if c.id == id:
                return c
        raise RuntimeError("Requested non-existing entry")

    def update(self, instance, validated_data):
        incoming_ids = validated_data.pop("identifiers")

        instance = super().update(instance, validated_data)

        all_existing = instance.identifiers.all()

        # If any ids no longer exist delete them
        incoming_ids_ids = [
            incoming["id"] for incoming in incoming_ids if "id" in incoming
        ]
        existing_ids = [existing.id for existing in all_existing]
        for existing in existing_ids:
            if existing not in incoming_ids_ids:
                MemberIdentifier.objects.get(id=existing).delete()

        # If there is an id do an update, else do a create
        serializer = MemberIdentifierSerializer()
        for eachId in incoming_ids:
            if "id" not in eachId:
                MemberIdentifier.objects.create(member=instance, **eachId)
            else:
                serializer.update(self.get_existing(eachId["id"], all_existing), eachId)
        return instance


class MemberResponseSerializer(MemberBaseSerializer):

    profile = serializers.HyperlinkedIdentityField(
        read_only=True, view_name="member_profiles"
    )
    profile_thumbnail = serializers.HyperlinkedIdentityField(
        read_only=True, view_name="member_profile_thumbnails"
    )

    class Meta:
        model = Member
        fields = MemberBaseSerializer.Meta.fields + (
            "organizations",
            "profile_thumbnail",
        )
        read_only_fields = ("profile", "profile_thumbnail", "organizations")

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        if not instance.profile:
            rep["profile"] = None
        if not instance.profile_thumbnail:
            rep["profile_thumbnail"] = None
        return rep


class MemberDetailResponseSerializer(MemberResponseSerializer):

    permissions = serializers.SerializerMethodField("get_all_permissions")

    class Meta:
        model = Member
        fields = MemberResponseSerializer.Meta.fields + ("permissions",)
        read_only_fields = MemberResponseSerializer.Meta.read_only_fields + (
            "permissions",
        )

    def get_all_permissions(self, obj):
        return obj.get_all_permissions()


class MemberListSerializer(MemberBaseSerializer):
    class Meta:
        model = Member
        fields = MemberBaseSerializer.Meta.fields
        read_only_fields = MemberBaseSerializer.Meta.read_only_fields

    def to_representation(self, instance):
        return MemberResponseSerializer(context=self.context).to_representation(
            instance
        )


class MemberDetailSerializer(MemberBaseSerializer):
    class Meta:
        model = Member
        fields = MemberBaseSerializer.Meta.fields
        read_only_fields = MemberBaseSerializer.Meta.read_only_fields

    def to_representation(self, instance):
        return MemberDetailResponseSerializer(context=self.context).to_representation(
            instance
        )
