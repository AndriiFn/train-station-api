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


    def __str__(self):
            return (f"{self.route} departures at {self.departure_time}"
                    f" and arrivals at {self.arrival_time}")

    @property
    def duration_in_hours(self):
        duration = (self.arrival_time - self.departure_time)
        return f"{duration.total_seconds() / 3600} hours"

    @property
    def formatted_departure_time(self):
        return self.departure_time.strftime("%d %B %Y, %I:%M %p")

    @property
    def formatted_arrival_time(self):
        return self.arrival_time.strftime("%d %B %Y, %I:%M %p")


class Train(models.Model):
    name = models.CharField(max_length=255)
    cargo_num = models.IntegerField(blank=True, null=True)
    places_in_cargo = models.IntegerField(validators=[MinValueValidator(0)], default=1)
    train_type = models.ForeignKey("TrainType", on_delete=models.CASCADE, related_name="trains")

    def __str__(self):
        return self.name


class TrainType(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Ticket(models.Model):
    cargo = models.IntegerField(null=True, blank=True)
    seat = models.IntegerField(validators=[MinValueValidator(1)])
    journey = models.ForeignKey("Journey", on_delete=models.CASCADE, related_name="tickets")
    order = models.ForeignKey("Order", on_delete=models.CASCADE, related_name="tickets")

    @staticmethod
    def validate_ticket(seat, cargo, train, error_to_raise):
        booked_seats = {ticket.seat for ticket in Ticket.objects.filter(journey__train=train)}
        if seat in booked_seats:
            raise error_to_raise({"seat": f"Seat number {seat} is already booked"})

        booked_cargos = {ticket.cargo for ticket in Ticket.objects.filter(journey__train=train)}
        if cargo is not None and cargo in booked_cargos:
            raise error_to_raise({"cargo": f"Cargo number {cargo} is already booked"})

        for ticket_attr_value, ticket_attr_name, train_attr_name, min_value in [
            (seat, "seat", "places_in_cargo", 1),
            (cargo if cargo is not None else 0, "cargo", "cargo_num", 0),
        ]:
            count_attrs = getattr(train, train_attr_name)
            if not (min_value <= ticket_attr_value <= count_attrs):
                raise error_to_raise(
                    {
                        ticket_attr_name: f"{ticket_attr_value} "
                                          f"number must be in available range: "
                                          f"({min_value}, {train_attr_name}):"
                                          f"({min_value}, {count_attrs})"
                    }
                )

    def clean(self):
        Ticket.validate_ticket(
            self.seat,
            self.cargo,
            self.journey.train,
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
        return f"Journey: {self.journey} (seat: {self.seat}"


class Order(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    class Meta:
        ordering = ["-created"]

    def __str__(self):
        return f"Order: {self.user} (created: {self.created})"
