import warnings
from collections import  OrderedDict

from django.db import models
from django.utils.encoding import force_str

from rest_framework import exceptions, serializers
from rest_framework.compat import coreapi, coreschema
from rest_framework.schemas.coreapi import AutoSchema


def field_to_schema(field):
    title = force_str(field.label) if field.label else ''

    description = ''
    if field.help_text:
        description = force_str(field.help_text)
    else:
        if field.label:
            description = force_str(field.label)

    if isinstance(field, (serializers.ListSerializer, serializers.ListField)):
        child_schema = field_to_schema(field.child)
        return coreschema.Array(
            items=child_schema,
            title=title,
            description=description
        )
    elif isinstance(field, serializers.DictField):
        return coreschema.Object(
            title=title,
            description=description
        )
    elif isinstance(field, serializers.Serializer):
        return coreschema.Object(
            properties=OrderedDict([
                (key, field_to_schema(value))
                for key, value
                in field.fields.items()
            ]),
            title=title,
            description=description
        )
    elif isinstance(field, serializers.ManyRelatedField):
        related_field_schema = field_to_schema(field.child_relation)

        return coreschema.Array(
            items=related_field_schema,
            title=title,
            description=description
        )
    elif isinstance(field, serializers.PrimaryKeyRelatedField):
        schema_cls = coreschema.String
        model = getattr(field.queryset, 'model', None)
        if model is not None:
            model_field = model._meta.pk
            if isinstance(model_field, models.AutoField):
                schema_cls = coreschema.Integer
        return schema_cls(title=title, description=description)
    elif isinstance(field, serializers.RelatedField):
        return coreschema.String(title=title, description=description)
    elif isinstance(field, serializers.MultipleChoiceField):
        return coreschema.Array(
            items=coreschema.Enum(enum=list(field.choices)),
            title=title,
            description=description
        )
    elif isinstance(field, serializers.ChoiceField):
        return coreschema.Enum(
            enum=list(field.choices),
            title=title,
            description=description
        )
    elif isinstance(field, serializers.BooleanField):
        return coreschema.Boolean(title=title, description=description)
    elif isinstance(field, (serializers.DecimalField, serializers.FloatField)):
        return coreschema.Number(title=title, description=description)
    elif isinstance(field, serializers.IntegerField):
        return coreschema.Integer(title=title, description=description)
    elif isinstance(field, serializers.DateField):
        return coreschema.String(
            title=title,
            description=description,
            format='date'
        )
    elif isinstance(field, serializers.DateTimeField):
        return coreschema.String(
            title=title,
            description=description,
            format='date-time'
        )
    elif isinstance(field, serializers.JSONField):
        return coreschema.Object(title=title, description=description)

    if field.style.get('base_template') == 'textarea.html':
        return coreschema.String(
            title=title,
            description=description,
            format='textarea'
        )

    return coreschema.String(title=title, description=description)


class ManualSchema(AutoSchema):

    def get_serializer_fields(self, path, method):
        """
        Return a list of `coreapi.Field` instances corresponding to any
        request body input, as determined by the serializer class.
        """
        view = self.view

        if method not in ('PUT', 'PATCH', 'POST'):
            return []

        if not hasattr(view, 'get_serializer'):
            return []

        try:
            serializer = view.get_serializer()
        except exceptions.APIException:
            serializer = None
            warnings.warn('{}.get_serializer() raised an exception during '
                          'schema generation. Serializer fields will not be '
                          'generated for {} {}.'
                          .format(view.__class__.__name__, method, path))

        if isinstance(serializer, serializers.ListSerializer):
            return [
                coreapi.Field(
                    name='data',
                    location='body',
                    required=True,
                    schema=coreschema.Array()
                )
            ]

        if not isinstance(serializer, serializers.Serializer):
            return []

        fields = []
        for field in serializer.fields.values():
            if field.read_only or isinstance(field, serializers.HiddenField):
                continue

            required = field.required and method != 'PATCH'
            field = coreapi.Field(
                name=field.field_name,
                location='form',
                required=required,
                schema=field_to_schema(field)
            )
            fields.append(field)
        return fields
