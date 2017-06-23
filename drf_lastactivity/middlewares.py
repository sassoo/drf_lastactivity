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

    def get_authenticated_user(self, request):
        """ Return a Django user model object """

        user = getattr(request, 'user', None)
        if user and user.is_authenticated():
            return user

    def process_response(self, request, response):
        """ Django override, return the response """

        user = self.get_authenticated_user(request)
        if user:
            self.update_last_login(user)
        return response

    def update_last_login(self, user):
        """ Update the user models LAST_LOGIN_FIELD """

        now = timezone.now()
        last = getattr(user, self.LAST_LOGIN_FIELD, None)
        if not last or (now - last).seconds > self.SPLAY_TIME:
            attrs = {self.LAST_LOGIN_FIELD: now}
            user.__class__.objects.filter(pk=user.pk).update(**attrs)
