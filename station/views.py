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
    TrainTypeSerializer,
    RouteListSerializer,
    RouteDetailSerializer,
    JourneyListSerializer,
    JourneyDetailListSerializer,
    TrainListSerializer,
    TrainDetailSerializer,
    OrderListSerializer,
)


def _params_to_ints(queryset):
    """Convert a list of string IDs to a list of integers."""
    return [int(str_id) for str_id in queryset.split(",") if str_id.isdigit()]


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all().select_related("source", "destination")
    serializer_class = RouteSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return RouteListSerializer
        elif self.action == "retrieve":
            return RouteDetailSerializer
        else:
            return RouteSerializer

    def get_queryset(self):
        """Retrieve routes with filters"""
        source = self.request.query_params.get("source")
        destination = self.request.query_params.get("destination")

        queryset = self.queryset

        if source:
            if source.isdigit():
                queryset = queryset.filter(source__id__in=source)
            else:
                queryset = queryset.filter(source__name__icontains=source)

        if destination:
            if destination.isdigit():
                queryset = queryset.filter(destination__id__in=destination)
            else:
                queryset = queryset.filter(destination__name__contains=destination)

        return queryset.distinct()


class StationViewSet(viewsets.ModelViewSet):
    queryset = Station.objects.all()
    serializer_class = StationSerializer

    def get_queryset(self):
        name = self.request.query_params.get("name")

        queryset = self.queryset

        if name:
            names = [city_name.strip() for city_name in name.split(",")]
            name_ids = _params_to_ints(name)
            city = [city_name.capitalize() for city_name in names if not city_name.isdigit()]

            if name_ids:
                queryset = queryset.filter(id__in=name_ids)

            if city:
                queryset = queryset.filter(name__in=city)

        return queryset.distinct()


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    serializer_class = CrewSerializer


class JourneyViewSet(viewsets.ModelViewSet):
    queryset = Journey.objects.all().select_related(
        "route__source",
        "route__destination",
        "train__train_type",
    )
    serializer_class = JourneySerializer

    def get_serializer_class(self):
        if self.action == "list":
            return JourneyListSerializer
        elif self.action == "retrieve":
            return JourneyDetailListSerializer
        else:
            return JourneySerializer

    def get_queryset(self):
        """Retrieve journey with filters"""
        source = self.request.query_params.get("source")
        destination = self.request.query_params.get("destination")
        train_name = self.request.query_params.get("train_name")

        queryset = self.queryset

        if source:
            if source.isdigit():
                queryset = queryset.filter(route__source__id__in=source)
            else:
                queryset = queryset.filter(route__source__name__icontains=source)

        if destination:
            if destination.isdigit():
                queryset = queryset.filter(route__destination__id__in=destination)
            else:
                queryset = queryset.filter(route__destination__name__icontains=destination)

        if train_name:
            if train_name.isdigit():
                queryset = queryset.filter(train__id__in=train_name)
            else:
                queryset = queryset.filter(train__name__icontains=train_name)

        return queryset.distinct()


class TrainViewSet(viewsets.ModelViewSet):
    queryset = Train.objects.all()
    serializer_class = TrainSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return TrainListSerializer
        elif self.action == "retrieve":
            return TrainDetailSerializer
        else:
            return TrainSerializer

    def get_queryset(self):
        name = self.request.query_params.get("name")
        train_type = self.request.query_params.get("train_type")

        queryset = self.queryset

        if name:
            name_ids = _params_to_ints(name)
            queryset = queryset.filter(id__in=name_ids)

        if train_type:
            train_type_ids = _params_to_ints(train_type)
            queryset = queryset.filter(id__in=train_type_ids)

        return queryset.distinct()


class TrainTypeViewSet(viewsets.ModelViewSet):
    queryset = TrainType.objects.all()
    serializer_class = TrainTypeSerializer

    def get_queryset(self):
        name = self.request.query_params.get("name")

        queryset = self.queryset

        if name:
            name_ids = _params_to_ints(name)
            queryset = queryset.filter(id__in=name_ids)

        return queryset.distinct()


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.select_related("user").prefetch_related("tickets__journey__train")
    serializer_class = OrderSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer
        else:
            return OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
