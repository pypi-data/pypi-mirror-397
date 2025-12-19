"""
Datetime to words conversion module.

Combines date and time conversion into a single datetime converter.
"""

from datetime import datetime
from typing import Union, TYPE_CHECKING

if TYPE_CHECKING:
    from uzpreprocessor.date import UzDateToWords
    from uzpreprocessor.time import UzTimeToWords


class UzDateAndTimeToWords:
    """
    Uzbek (Latin) datetime-to-words converter.
    
    Combines date and time conversion into a single converter.
    
    Examples:
        >>> from uzpreprocessor import UzNumberToWords, UzDateToWords, UzTimeToWords
        >>> n = UzNumberToWords()
        >>> d = UzDateToWords(n)
        >>> t = UzTimeToWords(n)
        >>> converter = UzDateAndTimeToWords(d, t)
        >>> converter.datetime("2025-09-18T14:35:08")
        'ikki ming yigirma beshinchi yil o'n sakkizinchi sentabr o'n to'rt soat o'ttiz besh daqiqa sakkiz soniya'
    """
    
    __slots__ = ('date_converter', 'time_converter')
    
    def __init__(
        self,
        date_converter: "UzDateToWords",
        time_converter: "UzTimeToWords",
    ):
        """
        Initialize datetime converter.
        
        Args:
            date_converter: Instance of UzDateToWords
            time_converter: Instance of UzTimeToWords
        """
        self.date_converter = date_converter
        self.time_converter = time_converter
    
    def _parse_datetime(self, value: Union[str, datetime]) -> datetime:
        """
        Parse datetime from string or datetime object.
        
        Args:
            value: Datetime string or object
            
        Returns:
            Parsed datetime object
            
        Raises:
            ValueError: If format is unsupported
        """
        if isinstance(value, datetime):
            return value
        
        if not isinstance(value, str):
            raise ValueError(f"Unsupported datetime type: {type(value)}")
        
        raw = value.strip()
        
        # Try ISO format first (most common)
        try:
            # Handle Z timezone
            return datetime.fromisoformat(raw.replace("Z", "+00:00"))
        except ValueError:
            pass
        
        # Try common patterns
        patterns = [
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M:%S.%f",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M:%S.%f",
            "%d.%m.%Y %H:%M:%S",
            "%d/%m/%Y %H:%M:%S",
        ]
        
        for pattern in patterns:
            try:
                return datetime.strptime(raw, pattern)
            except ValueError:
                continue
        
        raise ValueError(f"Unsupported datetime format: {raw}")
    
    def datetime(self, value: Union[str, datetime]) -> str:
        """
        Convert datetime to words.
        
        Args:
            value: Datetime to convert (string or datetime object)
            
        Returns:
            Words representation combining date and time
            
        Example:
            >>> converter.datetime("2025-09-18T14:35:08")
            'ikki ming yigirma beshinchi yil o'n sakkizinchi sentabr o'n to'rt soat o'ttiz besh daqiqa sakkiz soniya'
        """
        dt = self._parse_datetime(value)
        
        date_part = self.date_converter.date(dt)
        time_part = self.time_converter.time(dt)
        
        return f"{date_part} {time_part}"
    
    def datetime_full(self, value: Union[str, datetime]) -> str:
        """
        Convert datetime to full words format.
        
        Args:
            value: Datetime to convert
            
        Returns:
            Full words representation with all components
        """
        dt = self._parse_datetime(value)
        
        date_part = self.date_converter.date(dt)
        time_part = self.time_converter.time_full(dt)
        
        return f"{date_part} {time_part}"
