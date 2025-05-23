from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from station.models import (
    Route,
    Station,
    Crew,
    Order,
    Journey,
    Train,
    TrainType
)
from station.serializers import (
    RouteSerializer,
    StationSerializer,
    CrewSerializer,
    OrderSerializer,
    JourneySerializer,
    TrainSerializer,
    TrainTypeSerializer,
    RouteListSerializer,
    RouteDetailSerializer,
    JourneyListSerializer,
    JourneyDetailSerializer,
    TrainListSerializer,
    TrainDetailSerializer,
    OrderListSerializer,
    StationListSerializer,
    StationImageSerializer,
    TrainImageSerializer,
)


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
                queryset = queryset.filter(destination__name__icontains=destination)

        return queryset.distinct()

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "source",
                type={"type": "string", "items": {"type": "number"}},
                description="Filter by source ID or name (ex. ?source=3 OR ?source=kyiv)",
            ),
            OpenApiParameter(
                "destination",
                type={"type": "string", "items": {"type": "number"}},
                description="Filter by destination ID or name (ex. ?destination=4 OR ?destination=dnipro)",
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        """Get list of routes"""
        return super().list(request, *args, **kwargs)


def _params_to_ints(queryset):
    """Convert a list of string IDs to a list of integers."""
    return [int(str_id) for str_id in queryset.split(",") if str_id.isdigit()]


class StationViewSet(viewsets.ModelViewSet):
    queryset = Station.objects.all()
    serializer_class = StationSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return StationListSerializer
        elif self.action == "upload_image":
            return StationImageSerializer
        else:
            return StationSerializer

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

    @action(
        methods=["POST"],
        detail=True,
        url_path="upload-image",
    )
    def upload_image(self, request, pk=None):
        station = self.get_object()
        serializer = self.get_serializer(station, data=request.data)

        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "name",
                type={"type": "string", "items": {"type": "number"}},
                description="Filter by city name or ID (ex. ?name=lviv OR ?name=2)",
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        """Get list of stations"""
        return super().list(request, *args, **kwargs)


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
            return JourneyDetailSerializer
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

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "source",
                type={"type": "string", "items": {"type": "number"}},
                description="Filter by source name or ID (ex. ?source=lviv OR ?source=2)",
            ),
            OpenApiParameter(
                "destination",
                type={"type": "string", "items": {"type": "number"}},
                description="Filter by destination name or ID (ex. ?destination=lviv OR ?destination=4)",
            ),
            OpenApiParameter(
                "train_name",
                type={"type": "string", "items": {"type": "number"}},
                description="Filter by train_name name or ID (ex. ?train_name=Kyiv Express OR ?train_name=1)",
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        """Get list of journeys"""
        return super().list(request, *args, **kwargs)


class TrainViewSet(viewsets.ModelViewSet):
    queryset = Train.objects.all()
    serializer_class = TrainSerializer

    def get_serializer_class(self):
        if self.action == "list":
            return TrainListSerializer
        elif self.action == "upload_image":
            return TrainImageSerializer
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

    @action(
        methods=["POST"],
        detail=True,
        url_path="upload-image",
    )
    def upload_image(self, request, pk=None):
        train = self.get_object()
        serializer = self.get_serializer(train, data=request.data)

        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "name",
                type={"type": "string", "items": {"type": "number"}},
                description="Filter by name ID (ex. ?name=2)",
            ),
            OpenApiParameter(
                "train_type",
                type={"type": "string", "items": {"type": "number"}},
                description="Filter by train_type name ID (ex. ?train_type=1)",
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        """Get list of trains"""
        return super().list(request, *args, **kwargs)


class TrainTypeViewSet(viewsets.ModelViewSet):
    queryset = TrainType.objects.all()
    serializer_class = TrainTypeSerializer

    def get_queryset(self):
        name_list = self.request.query_params.getlist("name")

        queryset = self.queryset

        if name_list:
            try:
                name_ids = [int(n) for n in name_list if n.isdigit()]
                if name_ids:
                    queryset = queryset.filter(id__in=name_ids)
            except ValueError:
                pass

        return queryset.distinct()

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "name",
                type={"type": "array", "items": {"type": "number"}},
                description="Filter by name ID (ex. ?name=1,2)",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        """Get list of train types"""
        return super().list(request, *args, **kwargs)


class OrderViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    GenericViewSet,
):
    queryset = Order.objects.select_related("user").select_related("tickets__journey__train")
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated, )

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer
        else:
            return OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).select_related(
            "user"
        ).prefetch_related(
            "tickets__journey__route__source",
            "tickets__journey__route__destination",
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
