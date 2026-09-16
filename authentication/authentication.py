from rest_framework_simplejwt.authentication import JWTAuthentication


class CustomCookieAuthentication(JWTAuthentication):
    """
    Custom authentication class that retrieves the JWT access token 
    from HttpOnly cookies instead of the Authorization header.
    Falls back to standard authentication if no cookie is found.
    """

    def authenticate(self, request):
        """
        Overwrites the authenticate method to extract the token from cookies,
        validate it, and return the authenticated user and token.
        """
        raw_token = request.COOKIES.get('access_token')

        if raw_token is None:
            return super().authenticate(request)

        try:
            validated_token = self.get_validated_token(raw_token)
            return self.get_user(validated_token), validated_token
        except Exception:
            return None
