"""
    middlewares
    ~~~~~~~~~~~

    All of our custom DRF middlewares.
"""

from django.utils import timezone


class UpdateLastActivityMiddleware:
    """ Update the last_login timestamp every SPLAY_TIME (seconds)

    DRF doesn't take a stance here & I want something more
    frequent than every username & password submission.

    I want every access but obviously that would be a big
    performance hit so debounce the operation if the last
    update to the timestamp occurred < SPLAY_TIME in seconds.

    By default 5 minutes.
    """

    LAST_LOGIN_FIELD = 'last_login'
    SPLAY_TIME = 300

    def __init__(self, get_response):
        """ Reuquired by django 2.x middlewares """

        self.get_response = get_response

    def __call__(self, request):
        """ Taken directly from django's docs """

        # Code to be executed for each request before
        # the view (and later middleware) are called.
        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.
        user = self.get_authenticated_user(request)
        if user:
            self.update_last_login(user)

        return response

    def get_authenticated_user(self, request):
        """ Return an authenticated user model """

        if request.user and request.user.is_authenticated:
            return request.user
        return None

    def update_last_login(self, user):
        """ Update the user models LAST_LOGIN_FIELD """

        now = timezone.now()
        last = getattr(user, self.LAST_LOGIN_FIELD, None)
        if not last or (now - last).seconds > self.SPLAY_TIME:
            attrs = {self.LAST_LOGIN_FIELD: now}
            user.__class__.objects.filter(pk=user.pk).update(**attrs)
