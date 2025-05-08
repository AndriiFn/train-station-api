import uuid
from datetime import timedelta

from django.db.migrations import serializer
from django.utils import timezone

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from station.models import Train, Station, Route, Journey, TrainType
from station.serializers import JourneyDetailSerializer, JourneyListSerializer, TrainListSerializer, \
    TrainDetailSerializer


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

def sample_train_type(**params):
    defaults = {
        "name": f"sample train type",
    }
    defaults.update(params)

    return TrainType.objects.create(**defaults)

TRAIN_URL = reverse("station:train-list")

def detail_url(train_id):
    return reverse("station:train-detail", args=[train_id])


class UnauthenticatedTrainApiTests(TestCase):
    """Test for unauthenticated train API."""
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(TRAIN_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedTrainApiTests(TestCase):
    """Test for authenticated train API."""
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "user@user.com",
            "password123",
        )
        self.client.force_authenticate(self.user)

    def test_list_trains(self):
        sample_train()
        sample_train()

        res = self.client.get(TRAIN_URL)

        trains = Train.objects.order_by("id")
        serializer = TrainListSerializer(trains, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_train_detail(self):
        train = sample_train()

        url = detail_url(train.id)
        res = self.client.get(url)

        serializer = TrainDetailSerializer(train)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_train_forbidden(self):
        payload = {
            "name": "name",
            "cargo_num": 20,
            "places_in_cargo": 60,
            "train_type": sample_train_type(),
        }
        res = self.client.post(TRAIN_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_filter_by_name_or_train_type(self):
        train_type1 = sample_train_type(name="sample1")
        train_type2 = sample_train_type(name="sample2")

        train1 = sample_train(name=f"sample train 1", train_type=train_type1)
        train2 = sample_train(name=f"sample train 2", train_type=train_type2)

        res = self.client.get(TRAIN_URL, {"name": train1.id, "train_type": train_type1.id})

        serializer1 = TrainListSerializer(train1)
        serializer2 = TrainListSerializer(train2)

        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)


class AdminTrainApiTests(TestCase):
    """Test for admin train API."""
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@test.com",
            "password123",
            is_staff=True,
        )
        self.client.force_authenticate(self.user)

    def test_create_train_admin(self):
        train_type = sample_train_type()

        payload = {
            "name": "name",
            "cargo_num": 20,
            "places_in_cargo": 50,
            "train_type": train_type.id,
        }
        res = self.client.post(TRAIN_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        train = Train.objects.get(id=res.data["id"])
        self.assertEqual(train.name, payload["name"])
        self.assertEqual(train.cargo_num, payload["cargo_num"])
        self.assertEqual(train.places_in_cargo, payload["places_in_cargo"])
        self.assertEqual(train.train_type.id, train_type.id)
