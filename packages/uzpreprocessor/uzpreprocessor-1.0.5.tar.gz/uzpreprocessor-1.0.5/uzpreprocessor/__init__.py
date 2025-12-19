"""
UzPreprocessor - Uzbek Text Preprocessing Library

A comprehensive library for converting numbers, dates, times, currency,
and other formats to Uzbek (Latin) words. Perfect for legal documents,
invoices, and text processing.

Main Features:
    - Number to words conversion (integers, decimals, ordinals)
    - Currency conversion (so'm, tiyin)
    - Percentage conversion
    - Date to words conversion (multiple formats)
    - Time to words conversion (24h and AM/PM)
    - DateTime to words conversion
    - Automatic text processing with format detection
    - Number markers processing (№, #, No., etc.)

Example:
    >>> from uzpreprocessor import UzPreprocessor
    >>> processor = UzPreprocessor()
    >>> 
    >>> # Individual conversions
    >>> processor.number.number(123)
    'bir yuz yigirma uch'
    >>> processor.number.money(12345.67)
    "o'n ikki ming uch yuz qirq besh so'm oltmish yetti tiyin"
    >>> processor.date.date("2025-09-18")
    "ikki ming yigirma beshinchi yil o'n sakkizinchi sentabr"
    >>> 
    >>> # Automatic text processing
    >>> processor.process("Bugun 2025-09-18, narx: 12500 so'm")
    "Bugun ikki ming yigirma beshinchi yil o'n sakkizinchi sentabr, narx: o'n ikki ming besh yuz so'm"
"""

__version__ = "1.0.5"
__author__ = "Javhar Abdulatipov"
__email__ = "jakharbek@gmail.com"

from uzpreprocessor.number import UzNumberToWords
from uzpreprocessor.date import UzDateToWords
from uzpreprocessor.time import UzTimeToWords
from uzpreprocessor.datetime import UzDateAndTimeToWords
from uzpreprocessor.text import UzTextPreprocessor
from uzpreprocessor.math import UzMathToWords
from uzpreprocessor.processor import (
    UzTextProcessor,
    ProcessingConfig,
    ProcessingMode,
    TokenType,
    Token,
)

__all__ = [
    # Main classes
    "UzPreprocessor",
    "UzTextProcessor",

    # Individual converters
    "UzNumberToWords",
    "UzDateToWords",
    "UzTimeToWords",
    "UzDateAndTimeToWords",
    "UzTextPreprocessor",
    "UzMathToWords",

    # Configuration
    "ProcessingConfig",
    "ProcessingMode",
    "TokenType",
    "Token",
]


class UzPreprocessor:
    """
    Main convenience class that provides all conversion functionality.
    
    This class combines all converters into a single, easy-to-use interface.
    It provides both individual conversion methods and automatic text processing.
    
    Attributes:
        number: Number converter (UzNumberToWords)
        date: Date converter (UzDateToWords)
        time: Time converter (UzTimeToWords)
        datetime: DateTime converter (UzDateAndTimeToWords)
        text: Text marker preprocessor (UzTextPreprocessor)
        math: Math notation converter (UzMathToWords)
        processor: Automatic text processor (UzTextProcessor)
    
    Example:
        >>> processor = UzPreprocessor()
        >>> 
        >>> # Convert individual values
        >>> processor.number.number(123)
        'bir yuz yigirma uch'
        >>> processor.number.ordinal(5)
        'beshinchi'
        >>> processor.number.money(12345.67)
        "o'n ikki ming uch yuz qirq besh so'm oltmish yetti tiyin"
        >>> processor.date.date("2025-09-18")
        "ikki ming yigirma beshinchi yil o'n sakkizinchi sentabr"
        >>> processor.time.time("14:35")
        "o'n to'rt soat o'ttiz besh daqiqa"
        >>> 
        >>> # Process entire text automatically
        >>> processor.process("Sana: 2025-09-18, summa: 12500 so'm")
        "Sana: ikki ming yigirma beshinchi yil o'n sakkizinchi sentabr, summa: o'n ikki ming besh yuz so'm"
    """
    
    __slots__ = (
        '_number_converter',
        '_date_converter',
        '_time_converter',
        '_datetime_converter',
        '_text_preprocessor',
        '_math_converter',
        '_text_processor',
    )
    
    def __init__(self, config: ProcessingConfig = None):
        """
        Initialize all converters.

        Args:
            config: Optional configuration for text processing
        """
        # Initialize individual converters
        self._number_converter = UzNumberToWords()
        self._date_converter = UzDateToWords(self._number_converter)
        self._time_converter = UzTimeToWords(self._number_converter)
        self._datetime_converter = UzDateAndTimeToWords(
            self._date_converter,
            self._time_converter
        )
        self._text_preprocessor = UzTextPreprocessor(self._number_converter)
        self._math_converter = UzMathToWords(self._number_converter)

        # Initialize main text processor
        self._text_processor = UzTextProcessor(
            config=config,
            number_converter=self._number_converter,
            date_converter=self._date_converter,
            time_converter=self._time_converter,
            text_preprocessor=self._text_preprocessor,
            math_converter=self._math_converter,
        )
    
    # ========================================
    # INDIVIDUAL CONVERTERS
    # ========================================
    
    @property
    def number(self) -> UzNumberToWords:
        """Access the number converter."""
        return self._number_converter
    
    @property
    def date(self) -> UzDateToWords:
        """Access the date converter."""
        return self._date_converter
    
    @property
    def time(self) -> UzTimeToWords:
        """Access the time converter."""
        return self._time_converter
    
    @property
    def datetime(self) -> UzDateAndTimeToWords:
        """Access the datetime converter."""
        return self._datetime_converter
    
    @property
    def text(self) -> UzTextPreprocessor:
        """Access the text marker preprocessor."""
        return self._text_preprocessor

    @property
    def math(self) -> UzMathToWords:
        """Access the math notation converter."""
        return self._math_converter

    @property
    def processor(self) -> UzTextProcessor:
        """Access the automatic text processor."""
        return self._text_processor
    
    # ========================================
    # MAIN PROCESSING METHODS
    # ========================================
    
    def process(self, text: str, config: ProcessingConfig = None) -> str:
        """
        Process text and convert all detected formats to Uzbek words.
        
        This is the main method for automatic text processing. It detects
        and converts:
        - Numbers
        - Dates
        - Times
        - DateTimes
        - Currency amounts
        - Percentages
        - Number markers (№, #, No., etc.)
        - Uzbek suffixes (-chi, -son, etc.)
        
        Args:
            text: Input text to process
            config: Optional config override for this call
            
        Returns:
            Processed text with all formats converted to Uzbek words
            
        Example:
            >>> p = UzPreprocessor()
            >>> p.process("Bugun 2025-09-18, soat 14:35. Narx: 12500 so'm.")
            "Bugun ikki ming yigirma beshinchi yil o'n sakkizinchi sentabr, soat o'n to'rt soat o'ttiz besh daqiqa. Narx: o'n ikki ming besh yuz so'm."
        """
        return self._text_processor.process(text, config)
    
    def process_file(
        self, 
        input_path: str, 
        output_path: str = None,
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
        return self._text_processor.process_file(input_path, output_path, encoding)
    
    def analyze(self, text: str) -> dict:
        """
        Analyze text and return information about found patterns.
        
        Args:
            text: Input text to analyze
            
        Returns:
            Dictionary with analysis results including token counts and positions
        """
        return self._text_processor.analyze(text)
    
    # ========================================
    # CONVENIENCE METHODS
    # ========================================
    
    def numbers_only(self, text: str) -> str:
        """Process only numbers in text."""
        return self._text_processor.numbers_only(text)
    
    def dates_only(self, text: str) -> str:
        """Process only dates in text."""
        return self._text_processor.dates_only(text)
    
    def times_only(self, text: str) -> str:
        """Process only times in text."""
        return self._text_processor.times_only(text)
    
    def money_only(self, text: str) -> str:
        """Process only money amounts in text."""
        return self._text_processor.money_only(text)
