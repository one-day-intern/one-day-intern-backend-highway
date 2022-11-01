from django.test import TestCase
from rest_framework.reverse import reverse
from rest_framework.test import APIClient
from users.models import OdiUser, Assessee, AuthenticationService, Company, Assessor
from assessment.models import AssessmentEvent, Assignment, TestFlow, AssessmentEventSerializer
from .services import assessee_assessment_events
import datetime
import json
import pytz


class ViewsTestCase(TestCase):
    def setUp(self):
        self.url = reverse("assessee_dashboard")    # use the view url
        self.user = OdiUser.objects.create(email="complete@email.co", password="password")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_get(self):
        response = self.client.get(self.url)
        response.render()
        self.assertEquals(200, response.status_code)

        expected_content = {
            'past_events': [],
            'current_events': [],
            'future_events': [],
        }

        self.assertDictEqual(expected_content, json.loads(response.content))


class GetAssessmentEventTest(TestCase):
    def setUp(self) -> None:
        self.assessee = Assessee.objects.create_user(
            email='assessee_32@email.com',
            password='Password12334',
            first_name='Bambang',
            last_name='Haryono',
            phone_number='+62312334672',
            date_of_birth=datetime.date(2000, 11, 1),
            authentication_service=AuthenticationService.DEFAULT.value
        )

        self.company = Company.objects.create_user(
            email='gojek@gojek.com',
            password='Password12344',
            company_name='Gojek',
            description='A ride hailing application',
            address='Jl. The Gojek Street'
        )

        self.assessor = Assessor.objects.create_user(
            email='assessor51@gojek.com',
            password='Password12352',
            first_name='Robert',
            last_name='Journey',
            employee_id='AX123123',
            associated_company=self.company,
            authentication_service=AuthenticationService.DEFAULT.value
        )

        self.assignment = Assignment.objects.create(
            name='ASG Penelusuran Kasus',
            description='Menelusur kasus Korupsi PT A',
            owning_company=self.company,
            expected_file_format='pdf',
            duration_in_minutes=180
        )

        self.test_flow = TestFlow.objects.create(
            name='KPK Subdit 5 Lat 1',
            owning_company=self.company
        )
        self.test_flow.add_tool(
            assessment_tool=self.assignment,
            release_time=datetime.time(10, 30),
            start_working_time=datetime.time(10, 50)
        )

        self.assessment_event = AssessmentEvent.objects.create(
            name='Assessment Event 80',
            start_date_time=datetime.datetime(2022, 12, 12, hour=8, minute=0, tzinfo=pytz.utc),
            owning_company=self.company,
            test_flow_used=self.test_flow
        )
        self.expected_assessment_event = {
            'event_id': str(self.assessment_event.event_id),
            'name': self.assessment_event.name,
            'owning_company_id': str(self.company.company_id),
            'start_date_time': '2022-12-12T08:00:00Z',
            'test_flow_id': str(self.test_flow.test_flow_id)
        }

        self.assessment_event.add_participant(self.assessee, self.assessor)

        self.assessee_2 = Assessee.objects.create_user(
            email='assessee_98@email.com',
            password='Password123499',
            first_name='Bambang',
            last_name='Haryono',
            phone_number='+6231233467102',
            date_of_birth=datetime.date(2000, 11, 1),
            authentication_service=AuthenticationService.DEFAULT.value
        )

    def test_all_assessment_events_from_assessee_when_has_events(self):
        assessment_events = assessee_assessment_events.all_assessment_events(self.assessee)
        self.assertEquals(assessment_events, [self.assessment_event])

    def test_all_assessment_events_from_assessee_when_no_events(self):
        assessment_events = assessee_assessment_events.all_assessment_events(self.assessee_2)
        self.assertEquals(assessment_events, [])
