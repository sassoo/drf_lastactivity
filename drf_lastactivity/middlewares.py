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

    SPLAY_TIME = 300

    def process_response(self, request, response):
        """ Django override, return the response """

        user = getattr(request, 'user', None)
        if user and user.is_authenticated():
            now = timezone.now()
            last = user.last_login
            if not last or (now - last).seconds > self.SPLAY_TIME:
                user.__class__.objects.filter(pk=user.pk) \
                    .update(last_login=now)
        return response
