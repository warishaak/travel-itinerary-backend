from itineraries.domain.rules import validate_status_transition, validate_status_value


class ItineraryStatusService:
    """Use-case service for itinerary status updates and transitions."""

    @staticmethod
    def update_status(itinerary, new_status):
        validate_status_value(new_status)
        validate_status_transition(itinerary.status, new_status)
        itinerary.status = new_status
        itinerary.save(update_fields=["status", "updated_at"])
        return itinerary

    @staticmethod
    def validate_transition(current_status, new_status):
        validate_status_value(new_status)
        validate_status_transition(current_status, new_status)
