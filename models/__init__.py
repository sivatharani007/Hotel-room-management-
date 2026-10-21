# Models package initializer
from .customer import CustomerModel
from .room import RoomModel
from .booking import BookingModel
from .payment import PaymentModel

__all__ = ['CustomerModel', 'RoomModel', 'BookingModel', 'PaymentModel']
