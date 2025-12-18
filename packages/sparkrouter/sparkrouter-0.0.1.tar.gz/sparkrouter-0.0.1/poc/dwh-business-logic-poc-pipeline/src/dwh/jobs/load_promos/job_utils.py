from datetime import datetime
from zoneinfo import ZoneInfo


class JobUtils:

    @staticmethod
    def read_file(path: str) -> str:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()

    @staticmethod
    def parse_date_to_datetime(date_value: str, param_name: str) -> datetime:
        """
        Parse a date value to a datetime object with UTC timezone.

        Args:
            date_value: Date value to parse (string or datetime)
            param_name: Parameter name for error messages

        Returns:
            datetime: Parsed datetime with UTC timezone
        """
        # Debug the input type
        print(f"{param_name} type: {type(date_value)}, value: {date_value}")

        # Convert string dates to datetime objects if they are strings
        if isinstance(date_value, str):
            try:
                # Try ISO format first
                date_value = datetime.fromisoformat(date_value.replace('Z', '+00:00'))
            except ValueError as e1:
                print(f"ISO format parsing failed for {param_name}: {e1}")
                try:
                    # Try standard format
                    date_value = datetime.strptime(date_value, '%Y-%m-%d %H:%M:%S')
                except ValueError as e2:
                    print(f"Standard format parsing failed for {param_name}: {e2}")
                    try:
                        # Try date-only format
                        date_value = datetime.strptime(date_value, '%Y-%m-%d')
                    except ValueError as e3:
                        print(f"Date-only format parsing failed for {param_name}: {e3}")
                        raise ValueError(
                            f"Could not parse {param_name}: {date_value}. Please provide in format 'YYYY-MM-DD' or 'YYYY-MM-DD HH:MM:SS'")

                # Always add UTC timezone - this is critical
                date_value = date_value.replace(tzinfo=ZoneInfo('UTC'))
                print(f"Added UTC timezone to {param_name}: {date_value}")

        print(f"Converted {param_name}: {date_value}, tzinfo: {date_value.tzinfo}")

        # Ensure timezone is set even if parsing didn't add it
        if date_value.tzinfo is None:
            date_value = date_value.replace(tzinfo=ZoneInfo('UTC'))
            print(f"Forced UTC timezone on {param_name}: {date_value}")

        return date_value
