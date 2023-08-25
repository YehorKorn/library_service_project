from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdminOrIfIsAuthenticateCreateOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        return bool(
            (
                request.user
                and request.user.is_authenticated
                and request.method in ["POST", "GET"]
            )
            or (request.user and request.user.is_staff)
        )
