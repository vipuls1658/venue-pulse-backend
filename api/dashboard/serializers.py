from rest_framework import serializers


class VenueDetailSerializer(serializers.Serializer):
    """Validates that the venue-detail request carries a well-formed venue_id.

    Existence is intentionally NOT checked here: a missing venue is a 404 the
    view raises, while this serializer only guards the request shape (a 400).
    """

    venue_id = serializers.IntegerField(min_value=1)
