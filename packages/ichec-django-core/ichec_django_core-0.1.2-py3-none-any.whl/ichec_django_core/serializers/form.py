from rest_framework import serializers

from ..models import Form, FormField, FormFieldValue, FormGroup, PopulatedForm


class FormFieldSerializer(serializers.ModelSerializer):

    id = serializers.IntegerField(required=False)

    template = serializers.HyperlinkedIdentityField(
        read_only=True, view_name="form_field_templates"
    )

    class Meta:
        model = FormField
        fields = (
            "id",
            "label",
            "key",
            "required",
            "description",
            "template",
            "options",
            "default",
            "field_type",
            "order",
        )
        read_only_fields = ("id",)

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        if not instance.template:
            rep["template"] = None
        return rep


class FormGroupSerializer(serializers.ModelSerializer):

    fields = FormFieldSerializer(many=True)
    id = serializers.IntegerField(required=False)

    class Meta:
        model = FormGroup
        fields = (
            "id",
            "label",
            "description",
            "order",
            "fields",
        )
        read_only_fields = ("id",)

    def get_existing(self, id: str, collection: list):
        for c in collection:
            if c.id == id:
                return c
        raise RuntimeError("Requested non-existing entry")

    def update(self, instance, validated_data):

        fields = validated_data.pop("fields")

        instance = super().update(instance, validated_data)

        all_existing = instance.fields.all()

        # If any ids no longer exist delete them
        incoming_ids = [incoming["id"] for incoming in fields if "id" in incoming]
        existing_ids = [existing.id for existing in all_existing]
        for existing in existing_ids:
            if existing not in incoming_ids:
                FormField.objects.get(id=existing).delete()

        # If there is an id do an update, else do a create
        serializer = FormFieldSerializer()
        for field in fields:
            if "id" not in field:
                FormField.objects.create(group=instance, **field)
            else:
                serializer.update(self.get_existing(field["id"], all_existing), field)
        return instance


class FormSerializer(serializers.ModelSerializer):

    groups = FormGroupSerializer(many=True)
    id = serializers.IntegerField(required=False)

    class Meta:
        model = Form
        fields = ("groups", "id")
        read_only_fields = ("id",)

    def create(self, validated_data):
        groups = validated_data.pop("groups")

        instance = super().create(validated_data)

        for group in groups:
            fields = group.pop("fields")
            group_instance = FormGroup.objects.create(form=instance, **group)
            FormField.objects.bulk_create(
                [FormField(group=group_instance, **field) for field in fields]
            )
        return instance

    def get_existing(self, id: str, collection: list):
        for c in collection:
            if c.id == id:
                return c
        raise RuntimeError("Requested non-existing entry")

    def update(self, instance, validated_data):

        groups = validated_data.pop("groups")

        instance = super().update(instance, validated_data)

        all_existing = instance.groups.all()

        # If any ids no longer exist delete them
        incoming_ids = [incoming["id"] for incoming in groups if "id" in incoming]
        existing_ids = [existing.id for existing in all_existing]
        for existing in existing_ids:
            if existing not in incoming_ids:
                FormGroup.objects.get(id=existing).delete()

        # If there is an id do an update, else do a create
        serializer = FormGroupSerializer()
        for group in groups:
            if "id" not in group:
                FormGroup.objects.create(form=instance, **group)
            else:
                serializer.update(self.get_existing(group["id"], all_existing), group)
        return instance


class FormFieldValueDetailSerializer(serializers.ModelSerializer):

    field = FormFieldSerializer(read_only=True)
    id = serializers.IntegerField(required=False)
    asset = serializers.HyperlinkedIdentityField(
        read_only=True, view_name="form_field_value_assets"
    )

    class Meta:
        model = FormFieldValue
        fields = ("id", "value", "field", "asset")
        read_only_fields = ("id", "field")

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        if not instance.asset:
            rep["asset"] = None
        return rep


class FormFieldValueSerializer(serializers.ModelSerializer):

    id = serializers.IntegerField(required=False)

    class Meta:
        model = FormFieldValue
        fields = ("id", "value", "field")
        read_only_fields = ("id",)

    def to_representation(self, instance):
        return FormFieldValueDetailSerializer(context=self.context).to_representation(
            instance
        )


class PopulatedFormSerializer(serializers.ModelSerializer):

    values = FormFieldValueSerializer(many=True)
    id = serializers.IntegerField(required=False)

    class Meta:
        model = PopulatedForm
        fields = ("id", "values")
        read_only_fields = ("id",)

    def create(self, validated_data):
        values = validated_data.pop("values")

        instance = super().create(validated_data)

        FormFieldValue.objects.bulk_create(
            [FormFieldValue(form=instance, **value) for value in values]
        )
        return instance

    def get_existing(self, id: str, collection: list):
        for c in collection:
            if c.id == id:
                return c
        raise RuntimeError("Requested non-existing entry")

    def update(self, instance, validated_data):

        values = validated_data.pop("values")

        instance = super().update(instance, validated_data)

        all_existing = instance.values.all()

        # If any ids no longer exist delete them
        incoming_ids = [incoming["id"] for incoming in values if "id" in incoming]
        existing_ids = [existing.id for existing in all_existing]
        for existing in existing_ids:
            if existing not in incoming_ids:
                FormFieldValue.objects.get(id=existing).delete()

        # If there is an id do an update, else do a create
        serializer = FormFieldValueSerializer()
        for value in values:
            if "id" not in value:
                FormFieldValue.objects.create(form=instance, **value)
            else:
                serializer.update(self.get_existing(value["id"], all_existing), value)
        return instance
