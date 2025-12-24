class HealthSecureError(Exception):
    pass


class AuthenticationError(HealthSecureError):
    pass


class RateLimitError(HealthSecureError):
    pass


class APIError(HealthSecureError):
    pass

