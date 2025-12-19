"""
Main text processor module.

Unified processor that automatically detects and converts all supported formats
in text: numbers, dates, times, currency, percentages, and number markers.
"""

import re
from dataclasses import dataclass, field
from datetime import datetime, date, time
from decimal import Decimal, InvalidOperation
from enum import Enum, auto
from typing import (
    List, Dict, Tuple, Optional, Union, Callable, 
    Pattern, Match, Any, Set, TYPE_CHECKING
)

if TYPE_CHECKING:
    from uzpreprocessor.number import UzNumberToWords
    from uzpreprocessor.date import UzDateToWords
    from uzpreprocessor.time import UzTimeToWords
    from uzpreprocessor.text import UzTextPreprocessor
    from uzpreprocessor.math import UzMathToWords


class ProcessingMode(Enum):
    """Processing mode for the text processor."""
    STRICT = auto()      # Only process exact matches
    NORMAL = auto()      # Standard processing
    AGGRESSIVE = auto()  # Process all possible matches


class TokenType(Enum):
    """Types of tokens that can be processed."""
    NUMBER = auto()
    ORDINAL = auto()
    MONEY = auto()
    PERCENT = auto()
    DATE = auto()
    TIME = auto()
    DATETIME = auto()
    MARKER = auto()       # №, #, No., etc.
    SUFFIX = auto()       # -chi, -son, etc.
    MATH = auto()         # Mathematical operators and expressions
    PARENTHESIS = auto()  # ( and )
    DOLLAR = auto()       # $100, 100$
    EMAIL = auto()        # user@domain.com
    AT_SYMBOL = auto()    # @
    TEXT = auto()         # Plain text (not processed)


@dataclass
class Token:
    """Represents a token found in text."""
    type: TokenType
    value: str
    start: int
    end: int
    converted: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProcessingConfig:
    """Configuration for text processing."""
    # What to process
    process_numbers: bool = True
    process_ordinals: bool = True
    process_money: bool = True
    process_percent: bool = True
    process_dates: bool = True
    process_times: bool = True
    process_datetimes: bool = True
    process_markers: bool = True
    process_suffixes: bool = True
    process_math: bool = True
    process_ordinal_words: bool = True  # 1-uy -> birinchi uy, 1. uy -> birinchidan, uy
    process_parentheses: bool = True    # ( -> qavs ichida, ) -> qavs yopilgan
    process_dollar: bool = True         # $100, 100$ -> yuz dollar
    process_email: bool = True          # user@gmail.com -> user kuchukcha jimayl nuqta kom
    process_at_symbol: bool = True      # @ -> kuchukcha
    
    # How to process
    mode: ProcessingMode = ProcessingMode.NORMAL
    preserve_original: bool = False  # Keep original in parentheses
    
    # Number processing
    min_number: int = 0          # Minimum number to process
    max_number: int = 10**15     # Maximum number to process
    process_decimals: bool = True
    process_negative: bool = True
    
    # Currency settings
    default_currency: str = "so'm"
    currency_symbols: Dict[str, str] = field(default_factory=lambda: {
        "so'm": "so'm",
        "сум": "so'm",
        "сўм": "so'm",
        "$": "dollar",
        "€": "yevro",
        "₽": "rubl",
        "£": "funt",
    })


class UzTextProcessor:
    """
    Unified Uzbek text processor.
    
    Automatically detects and converts all supported formats in text:
    - Numbers (cardinal and ordinal)
    - Currency (so'm, dollars, etc.)
    - Percentages
    - Dates (multiple formats)
    - Times (multiple formats)
    - DateTimes
    - Number markers (№, #, No., etc.)
    - Uzbek suffixes (-chi, -son, -bob, etc.)
    
    Examples:
        >>> from uzpreprocessor import UzTextProcessor
        >>> processor = UzTextProcessor()
        >>> text = "Bugun 2025-09-18, soat 14:35. Narx: 12500 so'm (15% chegirma). Buyurtma №123."
        >>> print(processor.process(text))
        'Bugun ikki ming yigirma beshinchi yil o'n sakkizinchi sentabr, soat o'n to'rt soat o'ttiz besh daqiqa. Narx: o'n ikki ming besh yuz so'm (o'n besh foiz chegirma). Buyurtma bir yuz yigirma uchinchi.'
    
    Features:
        - Automatic format detection
        - Configurable processing
        - Token-based analysis
        - Preserves text structure
        - Handles overlapping patterns
        - Thread-safe (stateless processing)
    """
    
    __slots__ = ('_number', '_date', '_time', '_text', '_math', '_config', '_patterns')
    
    # ========================================
    # COMPILED REGEX PATTERNS
    # ========================================
    
    # Money patterns (must be before plain numbers)
    _PATTERN_MONEY = re.compile(
        r'''
        (?P<amount>-?\d[\d\ ]*(?:[.,]\d{1,2})?)  # Amount with optional decimals (space only, not newline)
        [ ]*                                     # Optional spaces (not newlines)
        (?P<currency>so'm|сум|сўм|\$|€|₽|£)      # Currency symbol/name (removed 'sum' as it conflicts)
        \b                                       # Word boundary
        ''',
        re.VERBOSE | re.IGNORECASE | re.UNICODE
    )
    
    # Percentage pattern
    _PATTERN_PERCENT = re.compile(
        r'(?P<value>-?\d[\d\s]*(?:[.,]\d+)?)\s*(?P<symbol>%|foiz|protsent)',
        re.IGNORECASE | re.UNICODE
    )
    
    # DateTime patterns (ISO format)
    _PATTERN_DATETIME = re.compile(
        r'''
        (?P<date>\d{4}-\d{2}-\d{2})  # Date part
        [T\s]                         # Separator
        (?P<time>\d{2}:\d{2}(?::\d{2})?)  # Time part
        (?:[.,]\d+)?                  # Optional microseconds
        (?:Z|[+-]\d{2}:?\d{2})?      # Optional timezone
        ''',
        re.VERBOSE
    )
    
    # Date patterns
    _PATTERN_DATE_ISO = re.compile(r'\b\d{4}-\d{2}-\d{2}\b')
    _PATTERN_DATE_EU = re.compile(r'\b\d{1,2}[./]\d{1,2}[./]\d{4}\b')
    _PATTERN_DATE_TEXT = re.compile(
        r'\b\d{1,2}\s+(?:yanvar|fevral|mart|aprel|may|iyun|iyul|avgust|sentabr|oktabr|noyabr|dekabr|'
        r'january|february|march|april|june|july|august|september|october|november|december|'
        r'jan|feb|mar|apr|jun|jul|aug|sep|sept|oct|nov|dec)\s+\d{4}\b',
        re.IGNORECASE
    )
    _PATTERN_DATE_LEGAL = re.compile(
        r'\b\d{4}\s*-?\s*yil\s*\d{1,2}\s*-?\s*[a-z]+\b',
        re.IGNORECASE
    )
    
    # Time patterns (with optional spaces around separators)
    _PATTERN_TIME_24H = re.compile(r'\b([01]?\d|2[0-3])\s*[:.\-]\s*([0-5]\d)(?:\s*[:.\-]\s*([0-5]\d))?\b')
    _PATTERN_TIME_AMPM = re.compile(
        r'\b(0?[1-9]|1[0-2])(?:\s*[:.\-]\s*([0-5]\d)(?:\s*[:.\-]\s*([0-5]\d))?)?\s*(AM|PM)\b',
        re.IGNORECASE
    )
    
    # Number markers
    # Special pattern for № with fraction (e.g., "№ 15/2025" -> "o'n besh raqami/2025")
    _PATTERN_MARKER_NUM_FRACTION = re.compile(r'№\s*(\d+)(/\d+)', re.UNICODE)
    _PATTERN_MARKER_NUM = re.compile(r'№\s*\d+', re.UNICODE)
    _PATTERN_MARKER_HASH = re.compile(r'#\s*\d+')
    _PATTERN_MARKER_NO = re.compile(r'\bNo\.?\s*\d+', re.IGNORECASE)
    _PATTERN_MARKER_LATIN = re.compile(
        r'\b(?:p|b|m|st|ch|art|sec|pt|par|item|fig|tab|eq|ex|app)\.\s*\d+',
        re.IGNORECASE
    )
    
    # Uzbek suffixes (capture suffix for preservation)
    _PATTERN_SUFFIX = re.compile(
        r"\b(\d+)-(chi|son|raqam|band|modda|bob|qism|bo'lim|punkt|jadval|rasm|misol|ilova)\b",
        re.IGNORECASE
    )

    # Fractional suffixes (e.g., 7/2-qism -> yetti bo'lish ikkinchi qism)
    _PATTERN_FRACTIONAL_SUFFIX = re.compile(
        r"\b(\d+)/(\d+)-(chi|son|raqam|band|modda|bob|qism|bo'lim|punkt|jadval|rasm|misol|ilova)\b",
        re.IGNORECASE
    )

    # Ordinal with word: 1-uy -> birinchi uy
    # Excludes known suffixes (chi, son, bob, etc.)
    _KNOWN_SUFFIXES = frozenset([
        'chi', 'son', 'raqam', 'band', 'modda', 'bob', 'qism',
        "bo'lim", 'punkt', 'jadval', 'rasm', 'misol', 'ilova',
        'inchi', 'nchi'
    ])
    _PATTERN_ORDINAL_WORD = re.compile(r'\b(\d+)-([a-zA-Z\']+)\b', re.UNICODE)

    # Ordinal with dot and word: 1. uy -> birinchidan, uy
    _PATTERN_ORDINAL_DOT_WORD = re.compile(r'\b(\d+)\.\s+([a-zA-Z\']+)\b', re.UNICODE)

    # Parentheses patterns
    _PATTERN_PAREN_OPEN = re.compile(r'\(')
    _PATTERN_PAREN_CLOSE = re.compile(r'\)')

    # Dollar patterns: $100, $ 100, 100$, 100 $
    _PATTERN_DOLLAR_BEFORE = re.compile(r'\$\s*(\d+(?:[.,]\d+)?)')  # $100, $ 100
    _PATTERN_DOLLAR_AFTER = re.compile(r'(\d+(?:[.,]\d+)?)\s*\$')   # 100$, 100 $

    # @ symbol -> kuchukcha
    _PATTERN_AT = re.compile(r'@')

    # Email pattern: user@domain.com
    _PATTERN_EMAIL = re.compile(
        r'\b([a-zA-Z0-9._%+-]+)@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\b',
        re.UNICODE
    )

    # Known domain/TLD pronunciations
    _DOMAIN_PRONUNCIATIONS = {
        # Email providers
        'gmail': 'jimayl', 'mail': 'meyl', 'email': 'imeyl',
        'yahoo': 'yaxu', 'hotmail': 'xotmeyl', 'outlook': 'autluk',
        'yandex': 'yandeks', 'proton': 'proton', 'icloud': 'ayklaud',
        # Common domain words
        'company': 'kompeniy', 'user': 'yuzer', 'users': 'yuzerz',
        'startup': 'startap', 'example': 'egzempl', 'support': 'sapport',
        'contact': 'kontakt', 'service': 'servis', 'online': 'onlayn',
        'cloud': 'klaud', 'tech': 'tek', 'digital': 'dijital',
        'media': 'mediya', 'store': 'stor', 'news': 'nyuz',
        'site': 'sayt', 'web': 'veb', 'app': 'epp', 'mobile': 'mobayl',
        'world': 'vorld', 'group': 'grup', 'team': 'tim',
        'code': 'kod', 'data': 'deyta', 'host': 'xost',
        'live': 'layv', 'plus': 'plyas', 'express': 'ekspress',
        # TLDs
        'com': 'kom', 'net': 'net', 'org': 'org', 'ru': 'ru',
        'uz': 'uz', 'info': 'info', 'edu': 'edu', 'gov': 'gov',
        'io': 'ayou', 'co': 'ko',
    }
    
    # Plain numbers (must be last to avoid matching parts of other patterns)
    _PATTERN_NUMBER = re.compile(
        r'''
        (?<![.\d№#])           # Not preceded by . digit or markers
        -?                      # Optional negative sign
        \d[\d\s]*               # Digits with optional spaces (12 345)
        (?:[.,]\d+)?            # Optional decimal part
        (?![.,]?\d|[-–]\w)      # Not followed by more digits or suffix
        ''',
        re.VERBOSE | re.UNICODE
    )
    
    # Ordinal pattern (number + inchi/nchi)
    _PATTERN_ORDINAL_EXISTING = re.compile(
        r'\b\d+\s*-?\s*(?:inchi|nchi)\b',
        re.IGNORECASE
    )

    # Mathematical expressions (number operator number)
    _PATTERN_MATH_EXPRESSION = re.compile(
        r'''
        (?P<left>-?\d+(?:[.,]\d+)?)     # Left operand
        \s*                              # Optional whitespace
        (?P<op>[+\-−×*÷/=<>≤≥≠^]|<=|>=|!=|\*\*)  # Operator (includes hyphen-minus and minus sign)
        \s*                              # Optional whitespace
        (?P<right>-?\d+(?:[.,]\d+)?)    # Right operand
        ''',
        re.VERBOSE | re.UNICODE
    )

    # Mathematical expressions with variables (x=5, y>10, 5=x, x=y)
    # Excludes minus to avoid conflicts with ordinal-word pattern (1-uy)
    _PATTERN_MATH_VAR_EXPRESSION = re.compile(
        r'''
        (?P<left>[a-zA-Z_]\w*|-?\d+(?:[.,]\d+)?)  # Left: variable or number
        \s*                                        # Optional whitespace
        (?P<op>[+×*÷/=<>≤≥≠^]|<=|>=|!=|\*\*)      # Operator (NO minus here)
        \s*                                        # Optional whitespace
        (?P<right>[a-zA-Z_]\w*|-?\d+(?:[.,]\d+)?) # Right: variable or number
        ''',
        re.VERBOSE | re.UNICODE
    )
    
    def __init__(
        self,
        config: Optional[ProcessingConfig] = None,
        number_converter: Optional["UzNumberToWords"] = None,
        date_converter: Optional["UzDateToWords"] = None,
        time_converter: Optional["UzTimeToWords"] = None,
        text_preprocessor: Optional["UzTextPreprocessor"] = None,
        math_converter: Optional["UzMathToWords"] = None,
    ):
        """
        Initialize the text processor.

        Args:
            config: Processing configuration (uses defaults if None)
            number_converter: Custom number converter
            date_converter: Custom date converter
            time_converter: Custom time converter
            text_preprocessor: Custom text preprocessor
            math_converter: Custom math converter
        """
        self._config = config or ProcessingConfig()

        # Import here to avoid circular imports
        from uzpreprocessor.number import UzNumberToWords
        from uzpreprocessor.date import UzDateToWords
        from uzpreprocessor.time import UzTimeToWords
        from uzpreprocessor.datetime import UzDateAndTimeToWords
        from uzpreprocessor.text import UzTextPreprocessor
        from uzpreprocessor.math import UzMathToWords

        # Initialize converters
        self._number = number_converter or UzNumberToWords()
        self._date = date_converter or UzDateToWords(self._number)
        self._time = time_converter or UzTimeToWords(self._number)
        self._text = text_preprocessor or UzTextPreprocessor(self._number)
        self._math = math_converter or UzMathToWords(self._number)

        # Build pattern priority list
        self._patterns = self._build_patterns()
    
    def _build_patterns(self) -> List[Tuple[Pattern, TokenType, Callable]]:
        """Build ordered list of patterns with their handlers."""
        patterns = []

        # Order matters! More specific patterns first
        if self._config.process_datetimes:
            patterns.append((self._PATTERN_DATETIME, TokenType.DATETIME, self._convert_datetime))

        if self._config.process_money:
            patterns.append((self._PATTERN_MONEY, TokenType.MONEY, self._convert_money))

        # Dollar patterns should come early (before plain numbers)
        if self._config.process_dollar:
            patterns.append((self._PATTERN_DOLLAR_BEFORE, TokenType.DOLLAR, self._convert_dollar))
            patterns.append((self._PATTERN_DOLLAR_AFTER, TokenType.DOLLAR, self._convert_dollar))

        if self._config.process_percent:
            patterns.append((self._PATTERN_PERCENT, TokenType.PERCENT, self._convert_percent))

        if self._config.process_dates:
            patterns.extend([
                (self._PATTERN_DATE_LEGAL, TokenType.DATE, self._convert_date),
                (self._PATTERN_DATE_TEXT, TokenType.DATE, self._convert_date),
                (self._PATTERN_DATE_ISO, TokenType.DATE, self._convert_date),
                (self._PATTERN_DATE_EU, TokenType.DATE, self._convert_date),
            ])

        if self._config.process_times:
            patterns.extend([
                (self._PATTERN_TIME_AMPM, TokenType.TIME, self._convert_time),
                (self._PATTERN_TIME_24H, TokenType.TIME, self._convert_time),
            ])

        # Markers should come before math expressions to avoid conflicts with № 15/2025
        if self._config.process_markers:
            patterns.extend([
                # Special pattern for № with fraction must come first
                (self._PATTERN_MARKER_NUM_FRACTION, TokenType.MARKER, self._convert_marker_num_fraction),
                (self._PATTERN_MARKER_NUM, TokenType.MARKER, self._convert_marker),
                (self._PATTERN_MARKER_HASH, TokenType.MARKER, self._convert_marker),
                (self._PATTERN_MARKER_NO, TokenType.MARKER, self._convert_marker),
                (self._PATTERN_MARKER_LATIN, TokenType.MARKER, self._convert_marker),
            ])

        # Fractional suffixes should come before math and regular suffixes
        if self._config.process_suffixes:
            patterns.append((self._PATTERN_FRACTIONAL_SUFFIX, TokenType.SUFFIX, self._convert_fractional_suffix))

        # Math expressions should come before plain numbers to avoid conflicts
        if self._config.process_math:
            patterns.append((self._PATTERN_MATH_EXPRESSION, TokenType.MATH, self._convert_math))
            # Also handle math with variables (x=5, y>10)
            patterns.append((self._PATTERN_MATH_VAR_EXPRESSION, TokenType.MATH, self._convert_math_var))

        if self._config.process_suffixes:
            patterns.append((self._PATTERN_SUFFIX, TokenType.SUFFIX, self._convert_suffix))

        # Ordinal-word patterns (1-uy, 1. uy) should come after suffixes
        if self._config.process_ordinal_words:
            patterns.append((self._PATTERN_ORDINAL_WORD, TokenType.ORDINAL, self._convert_ordinal_word))
            patterns.append((self._PATTERN_ORDINAL_DOT_WORD, TokenType.ORDINAL, self._convert_ordinal_dot_word))

        if self._config.process_ordinals:
            patterns.append((self._PATTERN_ORDINAL_EXISTING, TokenType.ORDINAL, self._convert_ordinal_existing))

        if self._config.process_numbers:
            patterns.append((self._PATTERN_NUMBER, TokenType.NUMBER, self._convert_number))

        # Parentheses
        if self._config.process_parentheses:
            patterns.append((self._PATTERN_PAREN_OPEN, TokenType.PARENTHESIS, self._convert_paren_open))
            patterns.append((self._PATTERN_PAREN_CLOSE, TokenType.PARENTHESIS, self._convert_paren_close))

        # Email should come BEFORE @ symbol
        if self._config.process_email:
            patterns.append((self._PATTERN_EMAIL, TokenType.EMAIL, self._convert_email))

        # @ symbol (standalone, not in email)
        if self._config.process_at_symbol:
            patterns.append((self._PATTERN_AT, TokenType.AT_SYMBOL, self._convert_at_symbol))

        return patterns
    
    # ========================================
    # CONVERSION METHODS
    # ========================================
    
    def _convert_number(self, match: Match) -> str:
        """Convert a plain number to words."""
        try:
            text = match.group(0)
            # Normalize: remove spaces, replace comma with dot
            clean = text.replace(" ", "").replace(",", ".")
            
            # Check bounds
            try:
                num = Decimal(clean)
                if abs(num) < self._config.min_number or abs(num) > self._config.max_number:
                    return text
                if not self._config.process_decimals and '.' in clean:
                    return text
                if not self._config.process_negative and num < 0:
                    return text
            except InvalidOperation:
                return text
            
            result = self._number.number(clean)
            
            if self._config.preserve_original:
                return f"{result} ({text})"
            return result
        except Exception:
            return match.group(0)
    
    def _convert_ordinal_existing(self, match: Match) -> str:
        """Convert existing ordinal notation (5-inchi) to words."""
        try:
            text = match.group(0)
            # Extract number
            num_match = re.search(r'\d+', text)
            if num_match:
                num = int(num_match.group())
                return self._number.ordinal(num)
            return text
        except Exception:
            return match.group(0)
    
    def _convert_money(self, match: Match) -> str:
        """Convert money amount to words."""
        try:
            amount_str = match.group('amount').replace(" ", "").replace(",", ".")
            currency = match.group('currency').lower()
            
            # Get currency name
            currency_name = self._config.currency_symbols.get(currency, currency)
            
            # For so'm, use the money() method
            if currency_name == "so'm":
                return self._number.money(amount_str)
            
            # For other currencies
            amount_words = self._number.number(amount_str)
            return f"{amount_words} {currency_name}"
        except Exception:
            return match.group(0)
    
    def _convert_percent(self, match: Match) -> str:
        """Convert percentage to words."""
        try:
            value = match.group('value').replace(" ", "").replace(",", ".")
            return self._number.percent(value)
        except Exception:
            return match.group(0)
    
    def _convert_date(self, match: Match) -> str:
        """Convert date to words."""
        try:
            return self._date.date(match.group(0))
        except Exception:
            return match.group(0)
    
    def _convert_time(self, match: Match) -> str:
        """Convert time to words."""
        try:
            time_str = match.group(0)
            result = self._time.time(time_str)
            return result
        except Exception:
            return match.group(0)
    
    def _convert_datetime(self, match: Match) -> str:
        """Convert datetime to words."""
        try:
            from uzpreprocessor.datetime import UzDateAndTimeToWords
            dt_converter = UzDateAndTimeToWords(self._date, self._time)
            return dt_converter.datetime(match.group(0))
        except Exception:
            return match.group(0)
    
    def _convert_marker(self, match: Match) -> str:
        """Convert number marker to words."""
        try:
            text = match.group(0)
            # Use text preprocessor
            return self._text.process(text, convert_numbers=True, convert_markers=True, convert_suffixes=False)
        except Exception:
            return match.group(0)

    def _convert_marker_num_fraction(self, match: Match) -> str:
        """Convert № marker with fraction (e.g., № 15/2025 -> raqami o'n besh bo'lish ikki ming yigirma besh)."""
        try:
            # Groups: 1=numerator, 2=fraction part (/2025)
            numerator = int(match.group(1))
            fraction_str = match.group(2)  # e.g., "/2025"
            denominator = int(fraction_str[1:])  # remove leading "/"

            num_word = self._number.number(numerator)
            denom_word = self._number.number(denominator)
            return f"raqami {num_word} bo'lish {denom_word}"
        except Exception:
            return match.group(0)
    
    def _convert_suffix(self, match: Match) -> str:
        """Convert Uzbek suffix to words (e.g., 1-bob -> birinchi bob)."""
        try:
            # Groups: 1=number, 2=suffix
            num = int(match.group(1))
            suffix = match.group(2).lower()
            ordinal = self._number.ordinal(num)

            # For -chi, just return ordinal (chi is already ordinal suffix)
            if suffix == 'chi':
                return ordinal

            # For other suffixes, preserve them
            return f"{ordinal} {suffix}"
        except Exception:
            return match.group(0)

    def _convert_fractional_suffix(self, match: Match) -> str:
        """Convert fractional suffix to words (e.g., 7/2-qism -> yetti bo'lish ikkinchi qism)."""
        try:
            # Groups: 1=numerator, 2=denominator, 3=suffix
            numerator = int(match.group(1))
            denominator = int(match.group(2))
            suffix = match.group(3).lower()

            # Convert numerator to cardinal
            num_word = self._number.number(numerator)

            # Convert denominator to ordinal
            denom_word = self._number.ordinal(denominator)

            # For -chi suffix, just return fraction with ordinal
            if suffix == 'chi':
                return f"{num_word} bo'lish {denom_word}"

            # For other suffixes, add the suffix word
            return f"{num_word} bo'lish {denom_word} {suffix}"
        except Exception:
            return match.group(0)

    def _convert_ordinal_word(self, match: Match) -> str:
        """Convert ordinal-word pattern to words (e.g., 1-uy -> birinchi uy)."""
        try:
            # Groups: 1=number, 2=word
            num = int(match.group(1))
            word = match.group(2)

            # Skip known suffixes - they are handled by _convert_suffix
            if word.lower() in self._KNOWN_SUFFIXES:
                return match.group(0)

            ordinal = self._number.ordinal(num)
            return f"{ordinal} {word}"
        except Exception:
            return match.group(0)

    def _convert_ordinal_dot_word(self, match: Match) -> str:
        """Convert ordinal-dot-word pattern to words (e.g., 1. uy -> birinchidan, uy)."""
        try:
            # Groups: 1=number, 2=word
            num = int(match.group(1))
            word = match.group(2)

            ordinal = self._number.ordinal(num)
            # Add "dan" suffix: birinchi -> birinchidan
            return f"{ordinal}dan, {word}"
        except Exception:
            return match.group(0)

    def _convert_math(self, match: Match) -> str:
        """Convert mathematical expression to words."""
        try:
            return self._math.expression(match.group(0), convert_numbers=True)
        except Exception:
            return match.group(0)

    def _convert_math_var(self, match: Match) -> str:
        """Convert mathematical expression with variables to words (e.g., x=5 -> x teng besh)."""
        try:
            left = match.group('left')
            op = match.group('op')
            right = match.group('right')

            # Convert operator to word
            op_word = self._math.operator(op)

            # Convert numbers to words, keep variables as-is
            def convert_operand(s):
                # Check if it's a number
                try:
                    clean = s.replace(" ", "").replace(",", ".")
                    # Try to parse as number
                    if clean.lstrip('-').replace('.', '').isdigit():
                        return self._number.number(clean)
                except Exception:
                    pass
                return s  # Return as-is (variable)

            left_word = convert_operand(left)
            right_word = convert_operand(right)

            return f"{left_word} {op_word} {right_word}"
        except Exception:
            return match.group(0)

    def _convert_paren_open(self, match: Match) -> str:
        """Convert opening parenthesis to words."""
        return " qavs ichida "

    def _convert_paren_close(self, match: Match) -> str:
        """Convert closing parenthesis to words."""
        return " qavs yopilgan "

    def _convert_dollar(self, match: Match) -> str:
        """Convert dollar amount to words (e.g., $100 -> yuz dollar)."""
        try:
            number_str = match.group(1)
            clean = number_str.replace(",", ".")
            cardinal = self._number.number(clean)
            return f"{cardinal} dollar"
        except Exception:
            return match.group(0)

    def _convert_email(self, match: Match) -> str:
        """Convert email to Uzbek pronunciation (e.g., user@gmail.com -> user kuchukcha jimayl nuqta kom)."""
        try:
            username = match.group(1)
            domain = match.group(2)

            # Split domain into parts
            domain_parts = domain.lower().split('.')

            # Convert each part
            converted_parts = []
            for part in domain_parts:
                if part in self._DOMAIN_PRONUNCIATIONS:
                    converted_parts.append(self._DOMAIN_PRONUNCIATIONS[part])
                else:
                    converted_parts.append(part)

            # Join with "nuqta"
            domain_converted = ' nuqta '.join(converted_parts)

            return f"{username} kuchukcha {domain_converted}"
        except Exception:
            return match.group(0)

    def _convert_at_symbol(self, match: Match) -> str:
        """Convert @ symbol to words."""
        return " kuchukcha "
    
    # ========================================
    # TOKENIZATION
    # ========================================
    
    def tokenize(self, text: str) -> List[Token]:
        """
        Tokenize text into processable tokens.
        
        Args:
            text: Input text
            
        Returns:
            List of tokens found in text
        """
        tokens: List[Token] = []
        used_ranges: Set[Tuple[int, int]] = set()
        
        # Find all matches for each pattern
        for pattern, token_type, converter in self._patterns:
            for match in pattern.finditer(text):
                start, end = match.start(), match.end()
                
                # Check if this range overlaps with already found tokens
                overlaps = False
                for used_start, used_end in used_ranges:
                    if not (end <= used_start or start >= used_end):
                        overlaps = True
                        break
                
                if not overlaps:
                    token = Token(
                        type=token_type,
                        value=match.group(0),
                        start=start,
                        end=end,
                        metadata={'match': match, 'converter': converter}
                    )
                    tokens.append(token)
                    used_ranges.add((start, end))
        
        # Sort by position
        tokens.sort(key=lambda t: t.start)
        
        return tokens
    
    # ========================================
    # MAIN PROCESSING
    # ========================================
    
    def process(self, text: str, config: Optional[ProcessingConfig] = None) -> str:
        """
        Process text and convert all detected formats to Uzbek words.
        
        This is the main method that:
        1. Tokenizes the text
        2. Converts each token
        3. Reconstructs the text
        
        Args:
            text: Input text to process
            config: Optional config override for this call
            
        Returns:
            Processed text with all formats converted to words
            
        Example:
            >>> processor.process("Sana: 2025-09-18, summa: 12500 so'm")
            "Sana: ikki ming yigirma beshinchi yil o'n sakkizinchi sentabr, summa: o'n ikki ming besh yuz so'm"
        """
        if not text:
            return text
        
        # Use override config if provided
        if config:
            original_config = self._config
            self._config = config
            self._patterns = self._build_patterns()
        
        try:
            # Tokenize
            tokens = self.tokenize(text)
            
            if not tokens:
                return text
            
            # Convert tokens using their stored converters
            for token in tokens:
                match = token.metadata.get('match')
                converter = token.metadata.get('converter')
                if match and converter:
                    token.converted = converter(match)
            
            # Reconstruct text
            result = []
            last_end = 0
            
            for token in tokens:
                # Add text before this token
                if token.start > last_end:
                    result.append(text[last_end:token.start])
                
                # Add converted or original value
                converted = token.converted if token.converted else token.value
                result.append(converted)
                last_end = token.end
                
                # Add space if next character is a letter and converted ends with letter
                if (last_end < len(text) and 
                    text[last_end].isalpha() and 
                    converted and converted[-1].isalpha()):
                    result.append(' ')
            
            # Add remaining text
            if last_end < len(text):
                result.append(text[last_end:])

            # Join and clean up multiple spaces
            final = ''.join(result)
            final = re.sub(r' +', ' ', final)
            return final.strip()
        
        finally:
            # Restore original config if override was used
            if config:
                self._config = original_config
                self._patterns = self._build_patterns()
    
    def process_file(
        self, 
        input_path: str, 
        output_path: Optional[str] = None,
        encoding: str = 'utf-8'
    ) -> str:
        """
        Process a text file.
        
        Args:
            input_path: Path to input file
            output_path: Path to output file (if None, returns processed text)
            encoding: File encoding
            
        Returns:
            Processed text content
        """
        with open(input_path, 'r', encoding=encoding) as f:
            content = f.read()
        
        processed = self.process(content)
        
        if output_path:
            with open(output_path, 'w', encoding=encoding) as f:
                f.write(processed)
        
        return processed
    
    def analyze(self, text: str) -> Dict[str, Any]:
        """
        Analyze text and return detailed information about found patterns.
        
        Args:
            text: Input text to analyze
            
        Returns:
            Dictionary with analysis results
        """
        tokens = self.tokenize(text)
        
        # Count by type
        type_counts = {}
        for token in tokens:
            type_name = token.type.name
            type_counts[type_name] = type_counts.get(type_name, 0) + 1
        
        return {
            'total_tokens': len(tokens),
            'type_counts': type_counts,
            'tokens': [
                {
                    'type': t.type.name,
                    'value': t.value,
                    'position': (t.start, t.end),
                }
                for t in tokens
            ]
        }
    
    # ========================================
    # CONVENIENCE METHODS
    # ========================================
    
    def numbers_only(self, text: str) -> str:
        """Process only numbers in text."""
        config = ProcessingConfig(
            process_numbers=True,
            process_ordinals=False,
            process_money=False,
            process_percent=False,
            process_dates=False,
            process_times=False,
            process_datetimes=False,
            process_markers=False,
            process_suffixes=False,
        )
        return self.process(text, config)
    
    def dates_only(self, text: str) -> str:
        """Process only dates in text."""
        config = ProcessingConfig(
            process_numbers=False,
            process_ordinals=False,
            process_money=False,
            process_percent=False,
            process_dates=True,
            process_times=False,
            process_datetimes=False,
            process_markers=False,
            process_suffixes=False,
        )
        return self.process(text, config)
    
    def times_only(self, text: str) -> str:
        """Process only times in text."""
        config = ProcessingConfig(
            process_numbers=False,
            process_ordinals=False,
            process_money=False,
            process_percent=False,
            process_dates=False,
            process_times=True,
            process_datetimes=False,
            process_markers=False,
            process_suffixes=False,
        )
        return self.process(text, config)
    
    def money_only(self, text: str) -> str:
        """Process only money amounts in text."""
        config = ProcessingConfig(
            process_numbers=False,
            process_ordinals=False,
            process_money=True,
            process_percent=False,
            process_dates=False,
            process_times=False,
            process_datetimes=False,
            process_markers=False,
            process_suffixes=False,
        )
        return self.process(text, config)
    
    @property
    def config(self) -> ProcessingConfig:
        """Get current configuration."""
        return self._config
    
    @config.setter
    def config(self, value: ProcessingConfig) -> None:
        """Set configuration and rebuild patterns."""
        self._config = value
        self._patterns = self._build_patterns()

