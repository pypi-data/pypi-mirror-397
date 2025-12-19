"""
Date to words conversion module.

Converts dates to Uzbek (Latin) words with support for multiple input formats.
"""

import re
from datetime import date, datetime
from functools import lru_cache
from typing import Union, Tuple, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from uzpreprocessor.number import UzNumberToWords


class UzDateToWords:
    """
    Uzbek (Latin) date-to-words converter.
    
    Supports multiple date formats:
    - ISO: 2025-09-18, 2025-09-18T14:35:08
    - European: 18.09.2025, 18/09/2025, 18-09-2025
    - US: 09/18/2025, 09-18-2025
    - Text (English): "18 September 2025", "September 18, 2025", "Sep 18 2025"
    - Text (Uzbek): "18 sentabr 2025", "sentabr 18 2025"
    - Legal (Uzbek): "2025-yil 18-sentabr", "2025 yil 18 sentabr"
    
    Examples:
        >>> from uzpreprocessor import UzNumberToWords
        >>> n = UzNumberToWords()
        >>> converter = UzDateToWords(n)
        >>> converter.date("2025-09-18")
        'ikki ming yigirma beshinchi yil o'n sakkizinchi sentabr'
    """
    
    __slots__ = ('n',)  # Only store number converter reference
    
    MONTHS: Tuple[str, ...] = (
        "yanvar", "fevral", "mart", "aprel", "may", "iyun",
        "iyul", "avgust", "sentabr", "oktabr", "noyabr", "dekabr"
    )
    
    # Optimized: Frozen dict for O(1) lookup of all month names
    MONTH_MAP = {
        # Uzbek
        "yanvar": 1, "fevral": 2, "mart": 3, "aprel": 4, "may": 5,
        "iyun": 6, "iyul": 7, "avgust": 8, "sentabr": 9,
        "oktabr": 10, "noyabr": 11, "dekabr": 12,
        
        # English full
        "january": 1, "february": 2, "march": 3, "april": 4,
        "june": 6, "july": 7, "august": 8,
        "september": 9, "october": 10, "november": 11, "december": 12,
        
        # English short
        "jan": 1, "feb": 2, "mar": 3, "apr": 4,
        "jun": 6, "jul": 7, "aug": 8,
        "sep": 9, "sept": 9,
        "oct": 10, "nov": 11, "dec": 12,
    }
    
    DATE_PATTERNS: Tuple[str, ...] = (
        "%Y-%m-%d",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%d.%m.%Y",
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%m/%d/%Y",
        "%m-%d-%Y",
        "%Y/%m/%d",
        "%Y.%m.%d",
    )
    
    # Optimized: Compile regex patterns once at class level
    _PATTERN_LEGAL = re.compile(
        r"(?P<year>\d{4})\s*[-\s]?\s*yil\s*[-\s]?\s*(?P<day>\d{1,2})\s*[-\s]?\s*(?P<month>[a-z]+)",
        re.IGNORECASE
    )
    _PATTERN_DAY_MONTH_YEAR = re.compile(
        r"(?P<day>\d{1,2})\s+(?P<month>[a-z]+)\s+(?P<year>\d{4})",
        re.IGNORECASE
    )
    _PATTERN_MONTH_DAY_YEAR = re.compile(
        r"(?P<month>[a-z]+)\s+(?P<day>\d{1,2})\s+(?P<year>\d{4})",
        re.IGNORECASE
    )
    
    def __init__(self, number_converter: "UzNumberToWords"):
        """
        Initialize date converter.
        
        Args:
            number_converter: Instance of UzNumberToWords for number conversion
        """
        self.n = number_converter
    
    def _parse_date(self, value: Union[str, date, datetime]) -> date:
        """
        Parse date from various input formats.
        
        Uses optimized parsing order:
        1. Direct date/datetime objects (fastest)
        2. ISO format (most common)
        3. Text formats with regex
        4. Numeric formats with strptime
        
        Args:
            value: Date as string, date, or datetime object
            
        Returns:
            Parsed date object
            
        Raises:
            ValueError: If date format is unsupported
        """
        # Fast path: direct types (no parsing needed)
        if isinstance(value, datetime):
            return value.date()
        
        if isinstance(value, date):
            return value
        
        if not isinstance(value, str):
            raise ValueError(f"Unsupported date type: {type(value)}")
        
        raw = value
        value_clean = value.strip()
        value_lower = value_clean.lower()
        
        # Normalize: remove commas (for: September 18, 2025)
        value_lower = value_lower.replace(",", "")
        
        # Try ISO format first (most common in APIs/databases)
        try:
            return datetime.fromisoformat(raw.replace("Z", "+00:00")).date()
        except (ValueError, AttributeError):
            pass
        
        # 1) Legal Uzbek format: 2025-yil 18-sentabr
        m = self._PATTERN_LEGAL.match(value_lower)
        if m:
            year = int(m.group("year"))
            day = int(m.group("day"))
            month_name = m.group("month").lower()
            
            if month_name in self.MONTH_MAP:
                return date(year, self.MONTH_MAP[month_name], day)
        
        # 2) Text format: 18 september 2025
        m = self._PATTERN_DAY_MONTH_YEAR.match(value_lower)
        if m:
            day = int(m.group("day"))
            year = int(m.group("year"))
            month_name = m.group("month").lower()
            
            if month_name in self.MONTH_MAP:
                return date(year, self.MONTH_MAP[month_name], day)
        
        # 3) Text format: september 18 2025
        m = self._PATTERN_MONTH_DAY_YEAR.match(value_lower)
        if m:
            day = int(m.group("day"))
            year = int(m.group("year"))
            month_name = m.group("month").lower()
            
            if month_name in self.MONTH_MAP:
                return date(year, self.MONTH_MAP[month_name], day)
        
        # 4) Classic numeric formats
        for pattern in self.DATE_PATTERNS:
            try:
                return datetime.strptime(value_lower, pattern).date()
            except ValueError:
                continue
        
        raise ValueError(f"Unsupported date format: {raw}")
    
    def date(self, value: Union[str, date, datetime]) -> str:
        """
        Convert date to words.
        
        Args:
            value: Date to convert (string, date, or datetime)
            
        Returns:
            Words representation of the date in format:
            "{year}inchi yil {day}inchi {month}"
            
        Example:
            >>> converter.date("2025-09-18")
            'ikki ming yigirma beshinchi yil o'n sakkizinchi sentabr'
        """
        d = self._parse_date(value)
        
        year_word = f"{self.n.ordinal(d.year)} yil"
        day_word = self.n.ordinal(d.day)
        month_word = self.MONTHS[d.month - 1]
        
        return f"{year_word} {day_word} {month_word}"
    
    def date_full(self, value: Union[str, date, datetime]) -> str:
        """
        Convert date to full words format (year, day, month all as cardinal).
        
        Args:
            value: Date to convert
            
        Returns:
            Full words representation
            
        Example:
            >>> converter.date_full("2025-09-18")
            'ikki ming yigirma besh yil o'n sakkiz sentabr'
        """
        d = self._parse_date(value)
        
        year_word = f"{self.n.number(d.year)} yil"
        day_word = self.n.number(d.day)
        month_word = self.MONTHS[d.month - 1]
        
        return f"{year_word} {day_word} {month_word}"
