from django.db import models

from train_station_service import settings


class Route(models.Model):
    source = models.ForeignKey("Station", on_delete=models.CASCADE, related_name="sources")
    destination = models.ForeignKey("Station", on_delete=models.CASCADE, related_name="destinations")
    distance = models.IntegerField()


class Station(models.Model):
    name = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()


class Crew(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)


class Journey(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name="routes")
    train = models.ManyToManyField("Train", related_name="trains", on_delete=models.CASCADE)
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()


class Train(models.Model):
    name = models.CharField(max_length=255)
    cargo_num = models.IntegerField()
    train_type = models.ForeignKey("TrainType", on_delete=models.CASCADE, related_name="train_types")


class TrainType(models.Model):
    name = models.CharField(max_length=255)


class Ticket(models.Model):
    cargo = models.IntegerField()
    seat = models.IntegerField()
    journey = models.ForeignKey("Journey", on_delete=models.CASCADE, related_name="journeys")
    order = models.ForeignKey("Order", on_delete=models.CASCADE, related_name="orders")


class Order(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders")
