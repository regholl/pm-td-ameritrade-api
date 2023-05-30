from datetime import date, datetime
from pydantic import BaseModel

from td.utils.helpers import is_valid_iso_date_str, to_camel


class BaseApiModel(BaseModel):
    class Config:
        alias_generator = to_camel
        allow_population_by_field_name = True
        use_enum_values = True

    @staticmethod
    def validate_iso_date_field(value):
        invalid_msg = "Invalid date string format. Must be ISO YYYY-MM-DDTHH:MM:SS or YYYY-MM-DD format."
        if isinstance(value, datetime):
            return value.date().isoformat()
        elif isinstance(value, date):
            return value.isoformat()
        elif isinstance(value, str):
            if is_valid_iso_date_str(value):
                return value
            else:
                raise ValueError(invalid_msg)
        else:
            raise ValueError(invalid_msg)

    @staticmethod
    def validate_str_enum(value, enum_):
        if isinstance(value, str):
            if value not in enum_.all_values():
                raise ValueError(f"Invalid {value} for {enum_}")
        return value
