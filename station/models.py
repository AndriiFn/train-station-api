from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from train_station_service import settings


class Route(models.Model):
    source = models.ForeignKey("Station", on_delete=models.CASCADE, related_name="sources")
    destination = models.ForeignKey("Station", on_delete=models.CASCADE, related_name="destinations")
    distance = models.IntegerField(validators=[MinValueValidator(1)])

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["source", "destination"], name="unique_routes")
        ]

    def __str__(self):
        return f"Route: {self.source} -> {self.destination} ({self.distance} km)"


class Station(models.Model):
    name = models.CharField(max_length=255, unique=True)
    latitude = models.FloatField(
        validators=[MinValueValidator(-90), MaxValueValidator(90)]
    )
    longitude = models.FloatField(
        validators=[MinValueValidator(-180), MaxValueValidator(180)]
    )

    def __str__(self):
        return self.name


class Crew(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Journey(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name="journeys")
    train = models.ForeignKey("Train", on_delete=models.CASCADE, related_name="journeys")
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()

    def duration(self):
        return self.arrival_time - self.departure_time

    def __str__(self):
        return (f"{self.route} departures at {self.departure_time}"
                f" and arrivals at {self.arrival_time}")


class Train(models.Model):
    name = models.CharField(max_length=255)
    cargo_num = models.IntegerField(validators=[MinValueValidator(0)])
    places_in_cargo = models.IntegerField(validators=[MinValueValidator(0)])
    train_type = models.ForeignKey("TrainType", on_delete=models.CASCADE, related_name="trains")

    def __str__(self):
        return self.name


class TrainType(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Ticket(models.Model):
    cargo = models.IntegerField(validators=[MinValueValidator(0)])
    seat = models.IntegerField()
    journey = models.ForeignKey("Journey", on_delete=models.CASCADE, related_name="tickets")
    order = models.ForeignKey("Order", on_delete=models.CASCADE, related_name="orders")

    @staticmethod
    def validate_ticket(seat, cargo, places_in_cargo, error_to_raise):
        for ticket_attr_value, ticket_attr_name, places_in_cargo_attr_name in [
            (seat, "seat", "seats"),
            (cargo, "cargo", "cargos"),
        ]:
            count_attrs = getattr(places_in_cargo, places_in_cargo_attr_name)
            if not (1 <= ticket_attr_value <= count_attrs):
                raise error_to_raise(
                    {
                        ticket_attr_name: (
                            f"{ticket_attr_name} number must be in the available range: "
                            f"(1, {count_attrs})"
                        )
                    }
                )

    def clean(self):
        Ticket.validate_ticket(
            self.seat,
            self.cargo,
            self.journey.train.places_in_cargo,
            ValidationError
        )

    def save(
            self,
            *args,
            force_insert=False,
            force_update=False,
            using=None,
            update_fields=None,
    ):
        self.full_clean()
        return super(Ticket, self).save(
            force_insert, force_update, using, update_fields
        )


    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["cargo", "seat", "journey"],
                                    name="unique_ticket"),
        ]
        ordering = ["seat"]

    def __str__(self):
        return f"Journey: {self.journey} (seat: {self.seat}, cargo: {self.cargo})"


class Order(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders")

    class Meta:
        ordering = ["-created"]

    def __str__(self):
        return f"Order: {self.user} (created: {self.created})"
