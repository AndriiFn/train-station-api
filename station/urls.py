from django.urls import path, include
from rest_framework import routers

from station.views import (
    TrainViewSet,
    TrainTypeViewSet,
    RouteViewSet,
    StationViewSet,
    JourneyViewSet,
    CrewViewSet,
    OrderViewSet,
)

router = routers.DefaultRouter()
router.register("routes", RouteViewSet)
router.register("stations", StationViewSet)
router.register("trains", TrainViewSet)
router.register("train-types", TrainTypeViewSet)
router.register("journeys", JourneyViewSet)
router.register("crews", CrewViewSet)
router.register("orders", OrderViewSet)

urlpatterns = [
    path("", include(router.urls)),
]

app_name = "station"
