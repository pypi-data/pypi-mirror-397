"""
Time to words conversion module.

Converts time to Uzbek (Latin) words with support for multiple input formats
and spoken/formal modes.
"""

import re
from datetime import datetime, time
from functools import lru_cache
from typing import Union, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from uzpreprocessor.number import UzNumberToWords


class UzTimeToWords:
    """
    Uzbek (Latin) time-to-words converter.
    
    Modes:
    - Spoken mode (AM/PM present): Uses Uzbek time periods
      (ertalab, tushlikdan oldin, tushlikdan keyin, kechqurun, tun)
    - Formal mode (24-hour): Standard numeric format
    
    Supports multiple formats:
    - ISO: 14:35, 14:35:08, 14:35:08.123456
    - With separators: 14.35, 14-35, 14 35
    - AM/PM: 2 PM, 2:35 PM, 02:35 AM
    - With timezone: 14:35:08Z, 14:35:08+05:00
    - No separators: 1435, 143508
    
    Examples:
        >>> from uzpreprocessor import UzNumberToWords
        >>> n = UzNumberToWords()
        >>> converter = UzTimeToWords(n)
        >>> converter.time("14:35:08")
        'o'n to'rt soat o'ttiz besh daqiqa sakkiz soniya'
        >>> converter.time("2 PM")
        'tushlikdan keyin soat o'n to'rt'
    """
    
    __slots__ = ('n',)  # Only store number converter reference
    
    TIME_PATTERNS: Tuple[str, ...] = (
        # Standard formats
        "%H:%M",
        "%H:%M:%S",
        "%H:%M:%S.%f",
        # Alternative separators
        "%H-%M",
        "%H-%M-%S",
        "%H.%M",
        "%H.%M.%S",
        "%H %M",
        "%H %M %S",
        # AM / PM formats
        "%I:%M %p",
        "%I:%M:%S %p",
        "%I %p",
        "%I:%M%p",
        "%I%p",
        # No separators
        "%H%M",
        "%H%M%S",
    )
    
    # Optimized: Compile regex patterns once at class level
    _PATTERN_WHITESPACE = re.compile(r"\s+")
    _PATTERN_AMPM = re.compile(r"\b(AM|PM)\b", re.IGNORECASE)
    _PATTERN_TIMEZONE = re.compile(r"(Z|[+-]\d{2}:?\d{2})$")
    _PATTERN_COLON = re.compile(r"\s*:\s*")
    _PATTERN_DASH = re.compile(r"\s*-\s*")
    _PATTERN_DOT = re.compile(r"\s*\.\s*")
    _PATTERN_AMPM_SPACE = re.compile(r"\s*(AM|PM)\s*", re.IGNORECASE)
    
    # Optimized: Use tuple of tuples for period lookup (faster iteration)
    _SPOKEN_PERIODS: Tuple[Tuple[Tuple[int, int], str], ...] = (
        ((5, 10), "ertalab"),           # morning: 5:00-10:59
        ((11, 12), "tushlikdan oldin"), # before noon: 11:00-12:59
        ((13, 17), "tushlikdan keyin"), # afternoon: 13:00-17:59
        ((18, 22), "kechqurun"),        # evening: 18:00-22:59
        # default: tun (night): 23:00-4:59
    )
    
    def __init__(self, number_converter: "UzNumberToWords"):
        """
        Initialize time converter.
        
        Args:
            number_converter: Instance of UzNumberToWords for number conversion
        """
        self.n = number_converter
    
    def _normalize(self, text: str) -> Tuple[str, bool]:
        """
        Normalize time string for parsing.
        
        Optimized normalization:
        1. Detect AM/PM before modifications
        2. Remove timezone
        3. Normalize separators
        4. Clean up whitespace
        
        Args:
            text: Raw time string
            
        Returns:
            Tuple of (normalized_text, is_ampm)
        """
        # Strip and uppercase for consistent parsing
        text = text.strip().upper()
        
        # Normalize whitespace first
        text = self._PATTERN_WHITESPACE.sub(" ", text)
        
        # Detect AM/PM early (before destroying spaces)
        is_ampm = bool(self._PATTERN_AMPM.search(text))
        
        # Remove timezone suffixes (Z, +05:00, -0500)
        text = self._PATTERN_TIMEZONE.sub("", text)
        
        # Normalize separators: remove spaces around them
        text = self._PATTERN_COLON.sub(":", text)
        text = self._PATTERN_DASH.sub("-", text)
        text = self._PATTERN_DOT.sub(".", text)
        
        # Normalize AM/PM spacing: ensure single space before
        text = self._PATTERN_AMPM_SPACE.sub(r" \1", text)
        
        # Final cleanup
        text = self._PATTERN_WHITESPACE.sub(" ", text).strip()
        
        return text, is_ampm
    
    def _parse_time(self, value: Union[str, time, datetime]) -> Tuple[time, bool, int]:
        """
        Parse time from various input formats.

        Optimized parsing order:
        1. Direct time/datetime objects (fastest)
        2. ISO format
        3. Pattern matching

        Args:
            value: Time as string, time, or datetime object

        Returns:
            Tuple of (time_object, is_ampm, original_hour_12)
            original_hour_12 is the hour in 12-hour format (1-12) when is_ampm is True, otherwise 0

        Raises:
            ValueError: If time format is unsupported
        """
        # Fast path: direct types
        if isinstance(value, datetime):
            return value.time(), False, 0

        if isinstance(value, time):
            return value, False, 0

        if not isinstance(value, str):
            raise ValueError(f"Unsupported time type: {type(value)}")

        raw = value
        text, is_ampm = self._normalize(value)

        # Extract original 12-hour if AM/PM present
        original_hour_12 = 0
        if is_ampm:
            # Extract hour from AM/PM format before Python converts to 24h
            import re
            match = re.search(r'\b(\d{1,2})', text)
            if match:
                original_hour_12 = int(match.group(1))

        # Try ISO format first (most common)
        try:
            return time.fromisoformat(text), is_ampm, original_hour_12
        except (ValueError, AttributeError):
            pass

        # Try known patterns
        for pattern in self.TIME_PATTERNS:
            try:
                return datetime.strptime(text, pattern).time(), is_ampm, original_hour_12
            except ValueError:
                continue

        raise ValueError(f"Unsupported time format: {raw}")
    
    def _spoken_period(self, hour: int) -> str:
        """
        Get spoken period name for hour.
        
        Uzbek time periods:
        - ertalab (morning): 5:00-10:59
        - tushlikdan oldin (before noon): 11:00-12:59
        - tushlikdan keyin (afternoon): 13:00-17:59
        - kechqurun (evening): 18:00-22:59
        - tun (night): 23:00-4:59
        
        Args:
            hour: Hour (0-23)
            
        Returns:
            Period name in Uzbek
        """
        for (start, end), period in self._SPOKEN_PERIODS:
            if start <= hour <= end:
                return period
        return "tun"
    
    def time(self, value: Union[str, time, datetime]) -> str:
        """
        Convert time to words.

        Spoken mode (AM/PM present):
            "{period} soat {hour} [{minute} daqiqa] [{second} soniya]"

        Formal mode (24-hour):
            "{hour} soat [{minute} daqiqa] [{second} soniya]"

        Args:
            value: Time to convert (string, time, or datetime)

        Returns:
            Words representation of the time

        Example:
            >>> converter.time("14:35:08")
            'o'n to'rt soat o'ttiz besh daqiqa sakkiz soniya'
            >>> converter.time("2 PM")
            'tushlikdan keyin soat ikki'
        """
        t, is_ampm, original_hour_12 = self._parse_time(value)

        # Spoken mode (when AM/PM is present)
        if is_ampm:
            period = self._spoken_period(t.hour)
            # Use original 12-hour format hour instead of converted 24-hour
            hour_to_speak = original_hour_12 if original_hour_12 > 0 else t.hour
            parts = [period, "soat", self.n.number(hour_to_speak)]

            if t.minute:
                parts.append(self.n.number(t.minute))
                parts.append("daqiqa")

            if t.second:
                parts.append(self.n.number(t.second))
                parts.append("soniya")

            return " ".join(parts)
        
        # Formal mode (standard 24-hour format)
        parts = []

        # Always show hours
        if t.hour:
            parts.append(f"{self.n.number(t.hour)} soat")
        else:
            parts.append("nol soat")

        # Special handling for minutes when they are 00
        if t.minute == 0:
            parts.append("nol nol daqiqa")
        else:
            parts.append(f"{self.n.number(t.minute)} daqiqa")

        # Only show seconds if non-zero
        if t.second:
            parts.append(f"{self.n.number(t.second)} soniya")

        return " ".join(parts)
    
    def time_full(self, value: Union[str, time, datetime]) -> str:
        """
        Convert time to full words format (always show all components).

        Args:
            value: Time to convert

        Returns:
            Full words representation with all components

        Example:
            >>> converter.time_full("14:35:08")
            'o'n to'rt soat o'ttiz besh daqiqa sakkiz soniya'
            >>> converter.time_full("14:00:00")
            'o'n to'rt soat nol daqiqa nol soniya'
        """
        t, _, _ = self._parse_time(value)

        hour_word = self.n.number(t.hour)
        minute_word = self.n.number(t.minute)
        second_word = self.n.number(t.second)

        return f"{hour_word} soat {minute_word} daqiqa {second_word} soniya"
