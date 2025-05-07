import uuid

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from station.models import Route, Station
from station.serializers import RouteListSerializer, RouteDetailSerializer

ROUTE_URL = reverse("station:route-list")
STATION_URL = reverse("station:station-list")


def sample_route(**params):
    """Make sure 'source' and 'destination' are unique."""
    source = sample_station(name=f"sample source {uuid.uuid4()}")
    destination = sample_station(name=f"sample destination {uuid.uuid4()}")

    defaults = {
        "source": source,
        "destination": destination,
        "distance": 200
    }
    defaults.update(params)

    return Route.objects.create(**defaults)

def sample_station(**params):
    defaults = {
        "name": "sample name",
        "latitude": 50,
        "longitude": 30
    }
    defaults.update(params)

    return Station.objects.create(**defaults)

def detail_url(route_id):
    return reverse("station:route-detail", args=[route_id])


class UnauthenticatedRouteApiTests(TestCase):
    """Test for unauthenticated route API."""
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(ROUTE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedRouteApiTests(TestCase):
    """Tests for authenticated route API."""
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "User@test.com"
            "password123"
        )
        self.client.force_authenticate(self.user)

    def test_list_routes(self):
        sample_route()
        sample_route()

        res = self.client.get(ROUTE_URL)

        routes = Route.objects.order_by("id")
        serializer = RouteListSerializer(routes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_route_detail(self):
        route = sample_route()

        url = detail_url(route.id)
        res = self.client.get(url)

        serializer = RouteDetailSerializer(route)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_route_forbidden(self):
        payload = {
            "source": f"sample source",
            "destination": "sample destination",
            "distance": 100
        }
        res = self.client.post(ROUTE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_filter_routes_by_source_and_destination(self):
        source = sample_station(name="source")
        destination = sample_station(name="destination")

        route = sample_route(
            source=source,
            destination=destination,
            distance=400
        )

        res = self.client.get(
            ROUTE_URL, {
                "source": f"{source.id}",
                "destination": f"{destination.id}"
            }
        )
        serializer = RouteListSerializer([route], many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer.data, res.data)


class AdminRouteApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@test.com",
            "password123",
            is_staff = True
        )
        self.client.force_authenticate(self.user)

    def test_create_route_admin(self):
        source = sample_station(name=f"sample source")
        destination = sample_station(name=f"sample destination")

        payload = {
            "source": source.id,
            "destination": destination.id,
            "distance": 100
        }
        res = self.client.post(ROUTE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        route = Route.objects.get(id=res.data["id"])
        self.assertEqual(route.source, source)
        self.assertEqual(route.destination, destination)
        self.assertEqual(route.distance, payload["distance"])
