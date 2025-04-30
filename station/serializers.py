from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from station.models import (
    Route,
    Station,
    Crew,
    Journey,
    Train,
    TrainType,
    Ticket,
    Order,
)


class RouteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")


class StationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = ("id", "name", "latitude", "longitude")


class StationListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Station
        fields = ("id", "name", )


class RouteListSerializer(RouteSerializer):
    source = StationListSerializer(read_only=True)
    destination = StationListSerializer(read_only=True)

    class Meta:
        model = Route
        fields = ("id", "source", "destination")


class RouteDetailSerializer(RouteSerializer):
    source = StationSerializer(read_only=True)
    destination = StationSerializer(read_only=True)

    class Meta:
        model = Route
        fields = ("id", "source", "destination", "distance")


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ("id", "first_name", "last_name", "full_name")


class JourneySerializer(serializers.ModelSerializer):
    class Meta:
        model = Journey
        fields = ("id", "route", "train", "departure_time", "arrival_time")


class TrainTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainType
        fields = ("id", "name")


class TrainSerializer(serializers.ModelSerializer):
    train_type = TrainTypeSerializer(read_only=True)

    class Meta:
        model = Train
        fields = ("id", "name", "cargo_num", "places_in_cargo", "train_type")


class TrainListSerializer(TrainSerializer):
    train_type = TrainTypeSerializer(read_only=True)

    class Meta:
        model = Train
        fields = ("id", "name", "train_type")


class JourneyListSerializer(JourneySerializer):
    route = RouteListSerializer(read_only=True)
    train = TrainListSerializer(read_only=True)
    duration = serializers.CharField(
        source="duration_in_hours",
        read_only=True,
    )
    departure_time = serializers.CharField(
        source="formatted_departure_time",
        read_only=True,
    )
    arrival_time = serializers.CharField(
        source="formatted_arrival_time",
        read_only=True,
    )

    class Meta:
        model = Journey
        fields = ("id", "route", "train", "departure_time", "arrival_time", "duration")


class JourneyDetailListSerializer(JourneySerializer):
    route = RouteListSerializer(read_only=True)
    train = TrainSerializer(read_only=True)
    duration = serializers.CharField(
        source="duration_in_hours",
        read_only=True,
    )
    departure_time = serializers.CharField(
        source="formatted_departure_time",
        read_only=True,
    )
    arrival_time = serializers.CharField(
        source="formatted_arrival_time",
        read_only=True,
    )

    class Meta:
        model = Journey
        fields = ("id", "route", "train", "departure_time", "arrival_time", "duration")


class TicketSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        data = super(TicketSerializer, self).validate(attrs=attrs)
        Ticket.validate_ticket(
            attrs["cargo"],
            attrs["seat"],
            attrs["places_in_cargo"].journey.train,
            ValidationError
        )
        return data

    class Meta:
        model = Ticket
        fields = ("id", "cargo", "seat", "journey", "order")


class OrderSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=False, allow_empty=False)

    class Meta:
        model = Order
        fields = ("id", "tickets", "created")

    def create(self, validated_data):
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets")
            order = Order.objects.create(**validated_data)
            for ticket_data in tickets_data:
                Ticket.objects.create(order=order, **ticket_data)
            return order
