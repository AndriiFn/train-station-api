import uuid

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from station.models import Station
from station.serializers import StationListSerializer, StationSerializer

STATION_URL = reverse("station:station-list")

def sample_station(**params):
    defaults = {
        "name": f"sample name {uuid.uuid4()}",
        "latitude": 50,
        "longitude": 30
    }
    defaults.update(params)

    return Station.objects.create(**defaults)

def detail_url(station_id):
    return reverse("station:station-detail", args=[station_id])


class UnauthenticatedStationApiTests(TestCase):
    """Test for unauthenticated route API."""
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(STATION_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedStationApiTests(TestCase):
    """Tests for authenticated route API."""
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "User@test.com"
            "password123"
        )
        self.client.force_authenticate(self.user)

    def test_list_stations(self):
        sample_station()
        sample_station()

        res = self.client.get(STATION_URL)

        stations = Station.objects.order_by("id")
        serializer = StationListSerializer(stations, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_station_detail(self):
        station = sample_station()

        url = detail_url(station.id)
        res = self.client.get(url)

        serializer = StationSerializer(station)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_station_forbidden(self):
        payload = {
            "name": "sample name",
            "latitude": 50,
            "longitude": 30
        }
        res = self.client.post(STATION_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_filter_stations_by_name(self):
        """Test filtering stations by name using an OR condition (multiple values)."""
        station1 = sample_station(name="Station1")
        station2 = sample_station(name="Station2")
        station3 = sample_station(name="no match")

        res = self.client.get(STATION_URL, {"name": "station1,station2"})

        serializer1 = StationListSerializer(station1)
        serializer2 = StationListSerializer(station2)
        serializer3 = StationListSerializer(station3)

        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)


class AdminStationApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@test.com",
            "password123",
            is_staff = True
        )
        self.client.force_authenticate(self.user)

    def test_create_station_admin(self):
        payload = {
            "name": "sample name",
            "latitude": 50,
            "longitude": 30
        }
        res = self.client.post(STATION_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        station = Station.objects.get(id=res.data["id"])
        for key in payload.keys():
            self.assertEqual(res.data[key], getattr(station, key))
