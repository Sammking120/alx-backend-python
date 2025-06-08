from rest_framework import permissions


class IsParticipantOfConversation(permissions.BasePermission):
    """
    Custom permission to only allow participants of a conversation to interact with it.
    """
    def has_permission(self, request, view) -> bool:
        return bool(request.user and request.user.is_authenticated)
    
    def has_object_permission(self, request, view, obj) -> bool:
        if request.method in ['GET', 'PUT', 'PATCH', 'DELETE']:
            return request.user in obj.participants.all()
        return False

