from forum.authentication.backend import OverrideFacebookBackend, OverrideLinkedinOAuth2Backend


def socialauth_backend_names(request):
    """ Add socialauth backend names.
    """
    return {
        'backend_name_facebook': OverrideFacebookBackend.name,
        'backend_name_linkedin': OverrideLinkedinOAuth2Backend.name,
    }