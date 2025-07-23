from django.core.exceptions import PermissionDenied

class OwnerOrManagerMixin:
    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.owner != request.user and not request.user.groups.filter(name='Менеджер').exists():
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)