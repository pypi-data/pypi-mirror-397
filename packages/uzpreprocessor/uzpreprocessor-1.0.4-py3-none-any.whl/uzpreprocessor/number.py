"""
Number to words conversion module.

Converts numbers, currency, and percentages to Uzbek (Latin) words.
"""

from decimal import Decimal, getcontext
from functools import lru_cache
from typing import Union, Tuple

# Set high precision for decimal calculations
getcontext().prec = 30


class UzNumberToWords:
    """
    Uzbek (Latin) number-to-words converter.
    
    Supports:
    - integers (arbitrary size)
    - decimals up to 12 digits
    - negative numbers
    - currency: so'm / tiyin
    - percentages
    - ordinal numbers (tartib son)
    
    Examples:
        >>> converter = UzNumberToWords()
        >>> converter.number(123)
        'bir yuz yigirma uch'
        >>> converter.number(123.456)
        'bir yuz yigirma uch butun to'rt yuz ellik olti mingdan'
        >>> converter.money(12345.67)
        'o'n ikki ming uch yuz qirq besh so'm oltmish yetti tiyin'
        >>> converter.percent(12.345)
        'o'n ikki butun uch yuz qirq besh mingdan foiz'
        >>> converter.ordinal(2)
        'ikkinchi'
    """
    
    __slots__ = ()  # No instance attributes needed, saves memory
    
    # Optimized: Use tuples for immutable lookup tables (faster than lists)
    UNITS: Tuple[str, ...] = (
        "nol", "bir", "ikki", "uch", "to'rt",
        "besh", "olti", "yetti", "sakkiz", "to'qqiz"
    )
    
    TENS: Tuple[str, ...] = (
        "", "o'n", "yigirma", "o'ttiz", "qirq",
        "ellik", "oltmish", "yetmish",
        "sakson", "to'qson"
    )
    
    HUNDREDS: Tuple[str, ...] = (
        "", "bir yuz", "ikki yuz", "uch yuz", "to'rt yuz",
        "besh yuz", "olti yuz", "yetti yuz",
        "sakkiz yuz", "to'qqiz yuz"
    )
    
    ORDERS: Tuple[str, ...] = (
        "ming",
        "million",
        "milliard",
        "trillion",
        "kvadrillion",
        "kvintillion",
    )
    
    # Optimized: Use tuple for O(1) index lookup (faster than dict for small sizes)
    FRACTION_ORDERS: Tuple[str, ...] = (
        "",  # 0 - not used
        "o'ndan",
        "yuzdan",
        "mingdan",
        "o'n mingdan",
        "yuz mingdan",
        "milliondan",
        "o'n milliondan",
        "yuz milliondan",
        "milliarddan",
        "o'n milliarddan",
        "yuz milliarddan",
        "trilliondan",
    )
    
    # Vowels for ordinal suffix handling
    _VOWELS = frozenset('aeiouAEIOU')
    
    # Special ordinal endings for words ending in vowels
    _ORDINAL_VOWEL_ENDINGS = {
        'i': 'nchi',   # ikki -> ikkinchi
        'a': 'nchi',   # yigirma -> yigirmanchi (but we use different rule)
    }
    
    def ordinal(self, value: int) -> str:
        """
        Convert number to ordinal form (tartib son).
        
        Handles proper Uzbek grammar for ordinal formation:
        - bir -> birinchi
        - ikki -> ikkinchi (not ikkiinchi)
        - uch -> uchinchi
        - to'rt -> to'rtinchi
        
        Args:
            value: Integer to convert
            
        Returns:
            Ordinal form with proper suffix
            
        Example:
            >>> converter.ordinal(1)
            'birinchi'
            >>> converter.ordinal(2)
            'ikkinchi'
            >>> converter.ordinal(5)
            'beshinchi'
        """
        word = self.number(value)
        
        if not word:
            return "nolinchi"
        
        # Get last character to determine suffix
        last_char = word[-1]
        
        # If ends with vowel (like 'ikki', 'olti', 'yetti', 'to'qqiz', 'yigirma', 'ellik', etc.)
        # In Uzbek: consonant + inchi, vowel + nchi
        if last_char in self._VOWELS or last_char == 'i':
            return f"{word}nchi"
        else:
            return f"{word}inchi"
    
    @lru_cache(maxsize=1000)
    def _triad_to_words(self, n: int) -> str:
        """
        Convert a three-digit number (0-999) to words.
        
        Cached for performance - common triads are reused frequently.
        
        Args:
            n: Integer between 0 and 999
            
        Returns:
            Words representation of the triad
        """
        if n == 0:
            return ""
        
        # Pre-calculate all parts at once (faster than multiple conditions)
        h, remainder = divmod(n, 100)
        t, u = divmod(remainder, 10)
        
        # Build result tuple (filter empty strings later)
        parts = (
            self.HUNDREDS[h] if h else "",
            self.TENS[t] if t else "",
            self.UNITS[u] if u else ""
        )
        
        # Join non-empty parts
        return " ".join(p for p in parts if p)
    
    @lru_cache(maxsize=1000)
    def _integer_to_words(self, n: int) -> str:
        """
        Convert an integer to words.
        
        Cached for performance.
        
        Args:
            n: Integer to convert (can be arbitrarily large)
            
        Returns:
            Words representation of the integer
        """
        if n == 0:
            return "nol"
        
        # Build triads list using divmod (slightly faster)
        triads = []
        num = n
        while num > 0:
            num, remainder = divmod(num, 1000)
            triads.append(remainder)
        
        # Process triads from highest to lowest order
        words = []
        num_triads = len(triads)
        
        for i in range(num_triads - 1, -1, -1):
            triad = triads[i]
            if triad == 0:
                continue
            
            triad_words = self._triad_to_words(triad)
            if triad_words:
                words.append(triad_words)
            
            # Add order name (ming, million, etc.)
            if i > 0 and i <= len(self.ORDERS):
                words.append(self.ORDERS[i - 1])
        
        return " ".join(words)
    
    def number(self, value: Union[int, float, str, Decimal]) -> str:
        """
        Convert a number to words (supports decimals up to 12 digits).
        
        Args:
            value: Number to convert (int, float, str, or Decimal)
            
        Returns:
            Words representation of the number
            
        Example:
            >>> converter.number(123.456)
            'bir yuz yigirma uch butun to'rt yuz ellik olti mingdan'
            >>> converter.number(-42)
            'minus qirq ikki'
            >>> converter.number(0)
            'nol'
        """
        # Fast path for integers
        if isinstance(value, int):
            if value == 0:
                return "nol"
            if value < 0:
                return f"minus {self._integer_to_words(-value)}"
            return self._integer_to_words(value)
        
        # Convert to Decimal for precision
        num = Decimal(str(value))
        
        if num == 0:
            return "nol"
        
        words = []
        
        # Handle negative numbers
        if num < 0:
            words.append("minus")
            num = abs(num)
        
        # Use format for consistent decimal representation
        s = format(num, 'f')
        
        # Split integer and fractional parts
        if '.' in s:
            int_part_str, frac_part_str = s.split('.', 1)
            # Remove trailing zeros and limit to 12 digits
            frac_part_str = frac_part_str.rstrip('0')[:12]
        else:
            int_part_str = s
            frac_part_str = ""
        
        int_part = int(int_part_str)
        words.append(self._integer_to_words(int_part))
        
        # Handle fractional part
        if frac_part_str:
            frac_len = len(frac_part_str)
            frac_number = int(frac_part_str)

            # Format: "butun mingdan to'rt yuz ellik olti" (order before fraction)
            words.append("butun")

            # Use tuple index (faster than dict lookup for small indices)
            if frac_len < len(self.FRACTION_ORDERS):
                words.append(self.FRACTION_ORDERS[frac_len])

            words.append(self._integer_to_words(frac_number))
        
        return " ".join(words)
    
    def money(self, amount: Union[int, float, str, Decimal]) -> str:
        """
        Convert currency amount to words (so'm / tiyin).
        
        Args:
            amount: Currency amount to convert
            
        Returns:
            Words representation with so'm and tiyin
            
        Example:
            >>> converter.money(12345.67)
            'o'n ikki ming uch yuz qirq besh so'm oltmish yetti tiyin'
            >>> converter.money(1000)
            'bir ming so'm'
            >>> converter.money(0.50)
            'nol so'm ellik tiyin'
        """
        # Convert to Decimal for precision
        amount_dec = Decimal(str(amount))
        
        words = []
        
        # Handle negative amounts
        if amount_dec < 0:
            words.append("minus")
            amount_dec = abs(amount_dec)
        
        s = format(amount_dec, 'f')
        
        # Split so'm and tiyin parts
        if '.' in s:
            som_str, tiyin_str = s.split('.', 1)
            # Ensure tiyin is exactly 2 digits (pad or truncate)
            tiyin_str = (tiyin_str + "00")[:2]
        else:
            som_str = s
            tiyin_str = "00"
        
        som = int(som_str)
        tiyin = int(tiyin_str)
        
        # Convert so'm
        words.append(self._integer_to_words(som))
        words.append("so'm")
        
        # Convert tiyin if present
        if tiyin > 0:
            words.append(self._integer_to_words(tiyin))
            words.append("tiyin")
        
        return " ".join(words)
    
    def percent(self, value: Union[int, float, str, Decimal]) -> str:
        """
        Convert percentage to words.
        
        Args:
            value: Percentage value to convert
            
        Returns:
            Words representation with 'foiz' suffix
            
        Example:
            >>> converter.percent(12.345)
            'o'n ikki butun uch yuz qirq besh mingdan foiz'
            >>> converter.percent(100)
            'bir yuz foiz'
        """
        return f"{self.number(value)} foiz"
    
    def cardinal(self, value: int) -> str:
        """
        Alias for number() - convert cardinal number to words.
        
        Args:
            value: Integer to convert
            
        Returns:
            Words representation of the cardinal number
        """
        return self.number(value)
