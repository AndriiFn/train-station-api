from rest_framework import viewsets

from station.models import (
    Route,
    Station,
    Ticket,
    Crew,
    Order,
    Journey,
    Train,
    TrainType
)
from station.serializers import (
    RouteSerializer,
    StationSerializer,
    TicketSerializer,
    CrewSerializer,
    OrderSerializer,
    JourneySerializer,
    TrainSerializer,
    TrainTypeSerializer
)


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all()
    serializer_class = RouteSerializer


class StationViewSet(viewsets.ModelViewSet):
    queryset = Station.objects.all()
    serializer_class = StationSerializer


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer


class JourneyViewSet(viewsets.ModelViewSet):
    queryset = Journey.objects.all()
    serializer_class = JourneySerializer


class TrainViewSet(viewsets.ModelViewSet):
    queryset = Train.objects.all()
    serializer_class = TrainSerializer


class TrainTypeViewSet(viewsets.ModelViewSet):
    queryset = TrainType.objects.all()
    serializer_class = TrainTypeSerializer


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
