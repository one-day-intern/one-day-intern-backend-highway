from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from one_day_intern.decorators import catch_exception_and_convert_to_invalid_request_decorator
from one_day_intern.settings import (
    GOOGLE_AUTH_CLIENT_SECRET,
    GOOGLE_AUTH_CLIENT_ID,
    GOOGLE_AUTH_GRANT_TYPE,
    GOOGLE_AUTH_TOKEN_URL
)
from one_day_intern.exceptions import (
    InvalidGoogleAuthCodeException,
    InvalidGoogleIDTokenException,
    EmailNotFoundException,
    InvalidRequestException,
    InvalidGoogleLoginException,
    InvalidRegistrationException
)
from rest_framework_simplejwt.tokens import RefreshToken
from ..models import OdiUser, Assessor, Assessee, AuthenticationService, CompanyOneTimeLinkCode
from . import utils
import requests
import time
import uuid


def google_get_id_token_from_auth_code(auth_code, redirect_uri):
    param_argument = {
        'client_id': GOOGLE_AUTH_CLIENT_ID,
        'client_secret': GOOGLE_AUTH_CLIENT_SECRET,
        'code': auth_code,
        'grant_type': GOOGLE_AUTH_GRANT_TYPE,
        'redirect_uri': redirect_uri
    }
    print("PARAM ARGUMENT", param_argument)
    parameterized_url = utils.parameterize_url(GOOGLE_AUTH_TOKEN_URL, param_argument)
    session = requests.Session()
    response = session.post(parameterized_url)
    response_data = response.json()
    print("RESPONSE DATA", response_data)
    try:
        return response_data['id_token']
    except KeyError:
        raise InvalidGoogleAuthCodeException('Id token is not retrieved due to a problem with the authentication code')


def google_get_profile_from_id_token(identity_token):
    google_request = google_requests.Request()
    time.sleep(1)
    identity_info = id_token.verify_oauth2_token(identity_token, google_request, GOOGLE_AUTH_CLIENT_ID)
    identity_is_valid = identity_info.get('sub')
    if not identity_is_valid:
        raise InvalidGoogleIDTokenException('Id token is invalid')

    return identity_info


@catch_exception_and_convert_to_invalid_request_decorator(exception_types=EmailNotFoundException)
def get_assessee_user_with_google_matching_data(user_data):
    user_email = user_data.get('email')
    found_assessee_with_google = Assessee.objects.filter(email=user_email,
                                                         authentication_service=AuthenticationService.GOOGLE.value)
    if found_assessee_with_google.exists():
        return found_assessee_with_google[0]

    raise EmailNotFoundException(
        f'Assessee registering with google login with {user_email} email is not found'
    )


@catch_exception_and_convert_to_invalid_request_decorator(exception_types=EmailNotFoundException)
def get_assessor_user_with_google_matching_data(user_data):
    user_email = user_data.get('email')
    found_assessor_with_google = Assessor.objects.filter(email=user_email,
                                                         authentication_service=AuthenticationService.GOOGLE.value)
    if found_assessor_with_google.exists():
        return found_assessor_with_google[0]

    raise EmailNotFoundException(
        f'Assessor registering with google login with {user_email} email is not found'
    )


def get_assessee_assessor_user_with_google_matching_data(user_data):
    user_email = user_data.get('email')
    found_assessor_with_google = Assessor.objects.filter(email=user_email,
                                                         authentication_service=AuthenticationService.GOOGLE.value)
    if found_assessor_with_google.exists():
        return found_assessor_with_google[0]
    found_assessee_with_google = Assessee.objects.filter(email=user_email,
                                                         authentication_service=AuthenticationService.GOOGLE.value)
    if found_assessee_with_google.exists():
        return found_assessee_with_google[0]

    raise EmailNotFoundException(
        f'Assessor or Assessee registering with google login with {user_email} email is not found.'
    )


def create_assessee_from_data_using_google_auth(user_data):
    user_email = user_data.get('email')
    first_name = user_data.get('given_name')
    last_name = user_data.get('family_name')

    assessee = Assessee(
        email=user_email,
        first_name=first_name,
        last_name=last_name,
        authentication_service=AuthenticationService.GOOGLE.value
    )
    assessee.save()
    return assessee


def login_or_register_assessee_with_google_data(user_data):
    user_email = user_data.get('email')
    found_users = OdiUser.objects.filter(email=user_email)

    if not found_users.exists():
        return create_assessee_from_data_using_google_auth(user_data)
    else:
        try:
            return get_assessee_user_with_google_matching_data(user_data)
        except InvalidRequestException:
            raise InvalidGoogleLoginException('User is registered through the One Day Intern login service')


def create_assessor_from_data_using_google_auth(user_data, otc_data):
    user_email = user_data.get('email')
    first_name = user_data.get('given_name')
    last_name = user_data.get('family_name')
    one_time_code = uuid.UUID(otc_data.get('one_time_code'))

    found_one_time_code = CompanyOneTimeLinkCode.objects.get(code=one_time_code)
    if not found_one_time_code:
        raise InvalidRegistrationException('Registration code is invalid')
    if not found_one_time_code.is_active:
        raise InvalidRegistrationException('Registration code is expired')

    associated_company = found_one_time_code.associated_company
    found_one_time_code.is_active = False
    found_one_time_code.save()

    assessor = Assessor(
        email=user_email,
        first_name=first_name,
        last_name=last_name,
        associated_company=associated_company,
        authentication_service=AuthenticationService.GOOGLE.value
    )
    assessor.save()
    return assessor


def register_assessor_with_google_data(user_data, otc_data):
    user_email = user_data.get('email')
    found_users = OdiUser.objects.filter(email=user_email)

    if not found_users.exists():
        return create_assessor_from_data_using_google_auth(user_data, otc_data)
    else:
        try:
            return get_assessor_user_with_google_matching_data(user_data)
        except InvalidRequestException:
            raise InvalidGoogleLoginException('User is registered through the One Day Intern login service')


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }
