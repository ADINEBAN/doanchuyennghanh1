"""Custom exception types used across the app."""


class AppError(Exception):
    """Base application exception."""


class AuthenticationError(AppError):
    """Authentication request failed."""


class ConfigurationError(AppError):
    """Configuration is missing or invalid."""


class CameraError(AppError):
    """Webcam operation failed."""


class PersistenceError(AppError):
    """Saving or loading persistent data failed."""
