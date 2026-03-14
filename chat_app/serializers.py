from rest_framework import serializers
from django.contrib.auth.models import User


# ── Group Serializers ─────────────────────────────────────────

class CreateGroupSerializer(serializers.Serializer):
    name       = serializers.CharField(max_length=100, allow_blank=False, trim_whitespace=True)
    member_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        required=False,
        default=list,
    )

    def validate_member_ids(self, value):
        """Ensure all supplied member IDs correspond to real users."""
        if value:
            existing_ids = set(
                User.objects.filter(id__in=value).values_list('id', flat=True)
            )
            missing = set(value) - existing_ids
            if missing:
                raise serializers.ValidationError(
                    f"The following user IDs do not exist: {sorted(missing)}"
                )
        return value


class GroupMemberActionSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(min_value=1)

    def validate_user_id(self, value):
        if not User.objects.filter(id=value).exists():
            raise serializers.ValidationError(f"User with id={value} does not exist.")
        return value


# ── Utility Serializers ───────────────────────────────────────

class SearchQuerySerializer(serializers.Serializer):
    q = serializers.CharField(
        max_length=150,
        allow_blank=True,
        required=False,
        default='',
        trim_whitespace=True,
    )
