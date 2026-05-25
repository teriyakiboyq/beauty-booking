"""Domain enums aligned with PostgreSQL types."""

from enum import StrEnum


class UserRole(StrEnum):
    CLIENT = "client"
    MASTER = "master"


class AppointmentStatus(StrEnum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
