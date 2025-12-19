"""
Mathematical notation to words conversion module.

Converts mathematical symbols and operators to Uzbek (Latin) words.
"""

import re
from typing import Dict, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from uzpreprocessor.number import UzNumberToWords


class UzMathToWords:
    """
    Uzbek (Latin) mathematical notation converter.

    Converts mathematical symbols and operators to words:
    - Basic operators: +, -, *, /, =
    - Comparison: <, >, ≤, ≥, ≠
    - Other: ±, ×, ÷, √, ^, %

    Examples:
        >>> from uzpreprocessor import UzNumberToWords
        >>> n = UzNumberToWords()
        >>> converter = UzMathToWords(n)
        >>> converter.expression("2 + 3")
        'ikki qo\'shish uch'
        >>> converter.expression("5 * 10")
        'besh ko\'paytirish o\'n'
        >>> converter.operator("+")
        'qo\'shish'
    """

    __slots__ = ('n',)

    # Mathematical operators mapping
    OPERATORS: Dict[str, str] = {
        # Basic arithmetic
        '+': "qo'shish",
        '−': "ayirish",  # minus sign (U+2212)
        '-': "ayirish",  # hyphen-minus
        '×': "ko'paytirish",
        '*': "ko'paytirish",
        '÷': "bo'lish",
        '/': "bo'lish",
        '=': "teng",

        # Comparison
        '<': "kichik",
        '>': "katta",
        '≤': "kichik yoki teng",
        '<=': "kichik yoki teng",
        '≥': "katta yoki teng",
        '>=': "katta yoki teng",
        '≠': "teng emas",
        '!=': "teng emas",

        # Other
        '±': "plyus-minus",
        '∓': "minus-plyus",
        '√': "ildiz",
        '^': "daraja",
        '**': "daraja",
        '∑': "yig'indi",
        '∏': "ko'paytma",
        '∫': "integral",
        '∂': "xususiy hosila",
        '∆': "delta",
        '∇': "nabla",
        '∞': "cheksizlik",
        '∝': "proporsional",
        '≈': "taxminan teng",
        '≡': "ayniy teng",
        '∈': "tegishli",
        '∉': "tegishli emas",
        '⊂': "qism to'plam",
        '⊃': "ustun to'plam",
        '∪': "birlashma",
        '∩': "kesishma",
        '∅': "bo'sh to'plam",
    }

    # Pattern to match mathematical expressions
    # Matches: number operator number
    _PATTERN_EXPRESSION = re.compile(
        r'''
        (?P<left>-?\d+(?:[.,]\d+)?)     # Left operand
        \s*                              # Optional whitespace
        (?P<op>[+\-×*÷/=<>≤≥≠^])       # Operator
        \s*                              # Optional whitespace
        (?P<right>-?\d+(?:[.,]\d+)?)    # Right operand
        ''',
        re.VERBOSE | re.UNICODE
    )

    # Pattern to match standalone operators
    _PATTERN_OPERATOR = re.compile(
        r'[+\-×*÷/=<>≤≥≠±∓√^∑∏∫∂∆∇∞∝≈≡∈∉⊂⊃∪∩∅]|(?:<=|>=|!=|\*\*)',
        re.UNICODE
    )

    def __init__(self, number_converter: "UzNumberToWords"):
        """
        Initialize math converter.

        Args:
            number_converter: Instance of UzNumberToWords for number conversion
        """
        self.n = number_converter

    def operator(self, symbol: str) -> str:
        """
        Convert a mathematical operator to words.

        Args:
            symbol: Mathematical operator symbol

        Returns:
            Word representation of the operator

        Example:
            >>> converter.operator("+")
            'qo\'shish'
            >>> converter.operator("≤")
            'kichik yoki teng'
        """
        symbol = symbol.strip()
        return self.OPERATORS.get(symbol, symbol)

    def expression(self, text: str, convert_numbers: bool = True) -> str:
        """
        Convert a mathematical expression to words.

        Converts expressions like "2 + 3" to "ikki qo'shish uch".
        If convert_numbers is False, keeps numbers as digits.

        Args:
            text: Mathematical expression
            convert_numbers: Whether to convert numbers to words

        Returns:
            Word representation of the expression

        Example:
            >>> converter.expression("2 + 3")
            'ikki qo\'shish uch'
            >>> converter.expression("5 * 10")
            'besh ko\'paytirish o\'n'
            >>> converter.expression("2 + 3", convert_numbers=False)
            '2 qo\'shish 3'
        """
        match = self._PATTERN_EXPRESSION.match(text.strip())

        if not match:
            # If no expression match, just replace operators
            return self.replace_operators(text)

        left = match.group('left')
        op = match.group('op')
        right = match.group('right')

        # Convert numbers if requested
        if convert_numbers:
            try:
                left = self.n.number(left)
            except Exception:
                pass

            try:
                right = self.n.number(right)
            except Exception:
                pass

        # Convert operator
        op_word = self.operator(op)

        return f"{left} {op_word} {right}"

    def replace_operators(self, text: str) -> str:
        """
        Replace all mathematical operators in text with words.

        Keeps numbers and other text unchanged, only replaces operators.

        Args:
            text: Text containing mathematical operators

        Returns:
            Text with operators replaced by words

        Example:
            >>> converter.replace_operators("x + y")
            'x qo\'shish y'
            >>> converter.replace_operators("a ≤ b")
            'a kichik yoki teng b'
        """
        def replace_op(match):
            symbol = match.group(0)
            return self.operator(symbol)

        return self._PATTERN_OPERATOR.sub(replace_op, text)

    def process(self, text: str, convert_numbers: bool = True) -> str:
        """
        Process text containing mathematical notation.

        This is the main processing method that handles both expressions
        and standalone operators.

        Args:
            text: Text to process
            convert_numbers: Whether to convert numbers in expressions

        Returns:
            Processed text

        Example:
            >>> converter.process("Formula: 2 + 3 = 5")
            'Formula: ikki qo\'shish uch teng besh'
        """
        # Try to match as expression first
        if self._PATTERN_EXPRESSION.search(text):
            # Replace all expressions
            result = []
            last_end = 0

            for match in self._PATTERN_EXPRESSION.finditer(text):
                # Add text before match
                result.append(text[last_end:match.start()])

                # Add converted expression
                expr = match.group(0)
                result.append(self.expression(expr, convert_numbers))

                last_end = match.end()

            # Add remaining text
            result.append(text[last_end:])

            return ''.join(result)
        else:
            # Just replace operators
            return self.replace_operators(text)
