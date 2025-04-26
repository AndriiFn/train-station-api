from django.contrib import admin

from station.models import (
    Ticket,
    Route,
    Station,
    Crew,
    Journey,
    Train,
    TrainType,
    Order,
)

admin.site.register(Ticket)
admin.site.register(Route)
admin.site.register(Station)
admin.site.register(Crew)
admin.site.register(Journey)
admin.site.register(Train)
admin.site.register(TrainType)
admin.site.register(Order)
