from django.contrib.auth.models import User
from datetime import time, datetime
from users.models import Company, Assessor
from one_day_intern.exceptions import RestrictedAccessException
from ..exceptions.exceptions import AssessmentToolDoesNotExist
from ..models import AssessmentTool


def sanitize_file_format(file_format: str):
    if file_format:
        return file_format.strip('.')


def get_time_from_date_time_string(iso_datetime) -> time:
    iso_datetime = iso_datetime.strip('Z')
    try:
        datetime_: datetime = datetime.fromisoformat(iso_datetime)
        return time(datetime_.hour, datetime_.minute)
    except ValueError:
        raise ValueError(f'{iso_datetime} is not a valid ISO date string')


def get_tool_from_id(tool_id) -> AssessmentTool:
    found_assessment_tools = AssessmentTool.objects.filter(assessment_id=tool_id)

    if found_assessment_tools:
        return found_assessment_tools[0]
    else:
        raise AssessmentToolDoesNotExist(f'Assessment tool with id {tool_id} does not exist')


def get_company_or_assessor_associated_company_from_user(user: User) -> Company:
    found_companies = Company.objects.filter(email=user.email)
    if found_companies:
        return found_companies[0]

    found_assessors = Assessor.objects.filter(email=user.email)
    if found_assessors:
        assessor = found_assessors[0]
        return assessor.associated_company

    raise RestrictedAccessException(f'User with email {user.email} is not a company or an assessor')