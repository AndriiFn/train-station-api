import uuid
from datetime import timedelta
from django.utils import timezone

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from station.models import Train, Station, Route, Journey, TrainType
from station.serializers import JourneyDetailSerializer, JourneyListSerializer

JOURNEY_URL = reverse("station:journey-list")
ROUTE_URL = reverse("station:route-list")


def sample_journey(**params):
    route = sample_route()
    train = sample_train()
    departure_time = timezone.now() + timedelta(hours=1)
    arrival_time = timezone.now() + timedelta(hours=3)

    defaults = {
        "route": route,
        "train": train,
        "departure_time": departure_time,
        "arrival_time": arrival_time,
    }
    defaults.update(params)

    return Journey.objects.create(**defaults)

def sample_route(**params):
    """Make sure 'source' and 'destination' are unique."""
    source = sample_station(name=f"sample source {uuid.uuid4()}")
    destination = sample_station(name=f"sample destination {uuid.uuid4()}")

    defaults = {
        "source": source,
        "destination": destination,
        "distance": 150
    }
    defaults.update(params)

    return Route.objects.create(**defaults)

def sample_train_type(**params):
    defaults = {
        "name": f"sample train type",
    }
    defaults.update(params)

    return TrainType.objects.create(**defaults)

def sample_station(**params):
    defaults = {
        "name": "sample name",
        "latitude": 50,
        "longitude": 30
    }
    defaults.update(params)

    return Station.objects.create(**defaults)

def sample_train(**params):
    train_type = sample_train_type(name=f"sample train type {uuid.uuid4()}")

    defaults = {
        "name": "sample name",
        "cargo_num": 20,
        "places_in_cargo": 50,
        "train_type": train_type
    }
    defaults.update(params)

    return Train.objects.create(**defaults)

def detail_url(journey_id):
    return reverse("station:journey-detail", args=[journey_id])


class UnauthenticatedJourneyApiTests(TestCase):
    """Test for unauthenticated journey API."""
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(ROUTE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedJourneyApiTests(TestCase):
    """Test for authenticated journey API."""
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "user1@test.com",
            "password123",
        )
        self.client.force_authenticate(self.user)

    def test_list_journeys(self):
        sample_journey()
        sample_journey()

        res = self.client.get(JOURNEY_URL)

        journeys = Journey.objects.order_by("id")
        serializer = JourneyListSerializer(journeys, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_journey_detail(self):
        journey = sample_journey()

        url = detail_url(journey.id)
        res = self.client.get(url)

        serializer = JourneyDetailSerializer(journey)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_journey_forbidden(self):
        payload = {
            "route": "sample route",
            "train": "sample train",
            "departure_time": timezone.now(),
            "arrival_time": timezone.now(),
        }
        res = self.client.post(JOURNEY_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_filter_journeys_by_source_and_destination_and_train_type(self):
        source1 = sample_station(name="sample source 1")
        source2 = sample_station(name="sample source 2")
        destination1 = sample_station(name="sample destination 1")
        destination2 = sample_station(name="sample destination 2")
        train_type1 = sample_train_type(name="sample train type 1")
        train_type2 = sample_train_type(name="sample train type 2")

        route1 = sample_route(source=source1, destination=destination1)
        route2 = sample_route(source=source2, destination=destination2)
        train1 = sample_train(train_type=train_type1)
        train2 = sample_train(train_type=train_type2)

        journey1 = sample_journey(route=route1, train=train1)
        journey2 = sample_journey(route=route2, train=train2)

        res = self.client.get(
            JOURNEY_URL, {
                "source": source1.id,
                "destination": destination1.id,
                "train": train1.id,
            }
        )

        serializer1 = JourneyListSerializer(journey1)
        serializer2 = JourneyListSerializer(journey2)

        self.assertTrue(Journey.objects.filter(route=route1, train=train1).exists())
        self.assertTrue(Journey.objects.filter(route=route2, train=train2).exists())
        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)


class AdminJourneyApiTests(TestCase):
    """Test for admin journey API."""
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "AdminUser@test.com",
            "password123",
            is_staff=True,
        )
        self.client.force_authenticate(self.user)

    def test_create_journey_admin(self):
        route = sample_route()
        train = sample_train()

        payload = {
            "route": route.id,
            "train": train.id,
            "departure_time": timezone.now(),
            "arrival_time": timezone.now(),
        }
        res = self.client.post(JOURNEY_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        journey = Journey.objects.get(id=res.data["id"])
        self.assertEqual(journey.route.id, route.id)
        self.assertEqual(journey.train.id, train.id)
        self.assertEqual(journey.departure_time, payload["departure_time"])
        self.assertEqual(journey.arrival_time, payload["arrival_time"])
