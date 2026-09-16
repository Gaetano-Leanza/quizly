from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .serializers import RegisterSerializer


class RegisterView(APIView):
    """
    API view to handle new user registrations.
    Allows unrestricted access (AllowAny) to create a new user account.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Validates the incoming registration data, creates the user, 
        and returns a success message or validation errors.
        """
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "User created successfully!"}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """
    API view to authenticate users and issue JWT access and refresh tokens
    stored securely inside HttpOnly cookies.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Validates username and password, generates tokens for the user,
        sets them as HttpOnly cookies, and returns user details.
        """
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)

        if user is not None:

            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            response_data = {
                "detail": "Login successfully!",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email
                }
            }

            response = Response(response_data, status=status.HTTP_200_OK)

            # 3. Cookies setzen
            response.set_cookie(
                key='access_token',
                value=access_token,
                httponly=True,
                secure=False,
                samesite='Lax',
                max_age=3600
            )
            response.set_cookie(
                key='refresh_token',
                value=refresh_token,
                httponly=True,
                secure=False,
                samesite='Lax',
                max_age=3600 * 24 * 7
            )

            return response
        else:
            return Response(
                {"detail": "Ungültige Anmeldedaten."},
                status=status.HTTP_401_UNAUTHORIZED
            )


class CookieTokenRefreshView(APIView):
    """
    API view to refresh the JWT access token using the refresh token 
stored inside the HttpOnly cookies.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Retrieves the refresh token from cookies, generates a new access token,
        and sets it in a new HttpOnly cookie.
        """
        refresh_token = request.COOKIES.get('refresh_token')

        if not refresh_token:
            return Response(
                {"detail": "Refresh Token fehlt."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        try:
            token = RefreshToken(refresh_token)
            access_token = str(token.access_token)

            response = Response(
                {"detail": "Token refreshed"},
                status=status.HTTP_200_OK
            )

            response.set_cookie(
                key='access_token',
                value=access_token,
                httponly=True,
                secure=False,
                samesite='Lax',
                max_age=3600
            )
            return response

        except Exception:
            return Response(
                {"detail": "Refresh Token ungültig."},
                status=status.HTTP_401_UNAUTHORIZED
            )


class LogoutView(APIView):
    """
    API view to handle secure user logout by clearing the authentication cookies.
    Requires the user to be authenticated.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Deletes the access and refresh token cookies from the client.
        """

        response = Response(
            {"detail": "Log-Out successfully! All Tokens will be deleted. Refresh token is now invalid."},
            status=status.HTTP_200_OK
        )

        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')

        return response
