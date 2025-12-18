from ...._schemas import ResponseBase


class GetLocationResponse(ResponseBase):
    city: str
    city_lat_long: str
    country_code: str
    country_name: str
    state: str

