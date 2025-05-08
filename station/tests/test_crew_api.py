from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from station.models import Crew
from station.serializers import CrewSerializer

CREW_URL = reverse("station:crew-list")

def sample_crew(**params):
    defaults = {
        "first_name": "Name",
        "last_name": "Last name",
    }
    defaults.update(params)

    return Crew.objects.create(**defaults)

def detail_url(crew_id):
    return reverse("station:crew-detail", args=[crew_id])


class UnauthenticatedCrewApiTests(TestCase):
    """Test for unauthenticated crew API."""
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(CREW_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedCrewApiTests(TestCase):
    """Tests for authenticated crew API."""
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "User@test.com"
            "password123"
        )
        self.client.force_authenticate(self.user)

    def test_list_crews(self):
        sample_crew()
        sample_crew()

        res = self.client.get(CREW_URL)

        stations = Crew.objects.order_by("id")
        serializer = CrewSerializer(stations, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_crew_detail(self):
        crew = sample_crew()

        url = detail_url(crew.id)
        res = self.client.get(url)

        serializer = CrewSerializer(crew)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_crew_forbidden(self):
        payload = {
            "first_name": "name",
            "last_name": "last name",
        }
        res = self.client.post(CREW_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminCrewApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@test.com",
            "password123",
            is_staff = True
        )
        self.client.force_authenticate(self.user)

    def test_create_crew_admin(self):
        payload = {
            "first_name": "name",
            "last_name": "last name",
        }
        res = self.client.post(CREW_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        station = Crew.objects.get(id=res.data["id"])
        for key in payload.keys():
            self.assertEqual(res.data[key], getattr(station, key))
