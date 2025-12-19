"""
Text preprocessing module.

Processes text to convert number markers (№1, #1, No.1, 1-chi, etc.) to Uzbek words.
"""

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from uzpreprocessor.number import UzNumberToWords


class UzTextPreprocessor:
    """
    Uzbek text preprocessor for converting number markers to words.
    
    Supports various number marker formats (Latin only):
    
    Number signs:
    - №1, №2, № 1, № 2 (numero sign before)
    - 1№, 2№, 1 №, 2 № (numero sign after)
    - #1, #2, # 1, # 2 (hash before)
    - 1#, 2#, 1 #, 2 # (hash after)
    
    Latin markers:
    - No.1, No 1, no.1, no 1 (number)
    - N.1, N 1, n.1, n 1 (number short)
    - p.1, p 1 (punkt)
    - b.1, b 1, b-1 (band/bob)
    - m.1, m 1 (modda)
    - st.1, st 1 (statya)
    - ch.1, ch 1 (chapter)
    - art.1, art 1 (article)
    - sec.1, sec 1 (section)
    - pt.1, pt 1 (point)
    - par.1, par 1 (paragraph)
    
    Ordinal suffixes:
    - 1-chi, 2-chi (ordinal suffix)
    - 1-son, 2-son (number suffix)
    - 1-raqam, 2-raqam (digit suffix)
    - 1-band, 2-band (band suffix)
    - 1-modda, 2-modda (article suffix)
    - 1-bob, 2-bob (chapter suffix)
    - 1-qism, 2-qism (part suffix)
    - 1-bo'lim, 2-bo'lim (section suffix)
    
    Examples:
        >>> from uzpreprocessor import UzNumberToWords
        >>> n = UzNumberToWords()
        >>> preprocessor = UzTextPreprocessor(n)
        >>> preprocessor.process("Bu №1 va #2 sonlar")
        'Bu bir raqami va ikkinchi sonlar'
        >>> preprocessor.process("No.15 art.3")
        'No. o'n beshinchi art. uchinchi'
    """
    
    # ========================================
    # NUMBER SIGN PATTERNS (№, #)
    # ========================================
    
    # № before number (№1, № 1)
    _PATTERN_NUM_BEFORE = re.compile(r'№\s*(\d+)', re.UNICODE)
    
    # № after number (1№, 1 №)
    _PATTERN_NUM_AFTER = re.compile(r'(\d+)\s*№', re.UNICODE)
    
    # # before number (#1, # 1)
    _PATTERN_HASH_BEFORE = re.compile(r'#\s*(\d+)', re.UNICODE)
    
    # # after number (1#, 1 #)
    _PATTERN_HASH_AFTER = re.compile(r'(\d+)\s*#', re.UNICODE)
    
    # ========================================
    # LATIN MARKER PATTERNS
    # ========================================
    
    _PATTERN_MARKERS = {
        # Number markers
        'No.': re.compile(r'\bNo\.\s*(\d+)', re.IGNORECASE),
        'No': re.compile(r'\bNo\s+(\d+)', re.IGNORECASE),
        'N.': re.compile(r'\bN\.\s*(\d+)', re.IGNORECASE),
        'N': re.compile(r'\bN\s+(\d+)(?!\w)', re.IGNORECASE),
        
        # Document markers
        'p.': re.compile(r'\bp\.\s*(\d+)', re.IGNORECASE),
        'b.': re.compile(r'\bb\.\s*(\d+)', re.IGNORECASE),
        'b-': re.compile(r'\bb-(\d+)', re.IGNORECASE),
        'm.': re.compile(r'\bm\.\s*(\d+)', re.IGNORECASE),
        'st.': re.compile(r'\bst\.\s*(\d+)', re.IGNORECASE),
        'ch.': re.compile(r'\bch\.\s*(\d+)', re.IGNORECASE),
        'art.': re.compile(r'\bart\.\s*(\d+)', re.IGNORECASE),
        'sec.': re.compile(r'\bsec\.\s*(\d+)', re.IGNORECASE),
        'pt.': re.compile(r'\bpt\.\s*(\d+)', re.IGNORECASE),
        'par.': re.compile(r'\bpar\.\s*(\d+)', re.IGNORECASE),
        'item.': re.compile(r'\bitem\.\s*(\d+)', re.IGNORECASE),
        'fig.': re.compile(r'\bfig\.\s*(\d+)', re.IGNORECASE),
        'tab.': re.compile(r'\btab\.\s*(\d+)', re.IGNORECASE),
        'eq.': re.compile(r'\beq\.\s*(\d+)', re.IGNORECASE),
        'ex.': re.compile(r'\bex\.\s*(\d+)', re.IGNORECASE),
        'app.': re.compile(r'\bapp\.\s*(\d+)', re.IGNORECASE),
    }
    
    # ========================================
    # UZBEK SUFFIX PATTERNS
    # ========================================
    
    _PATTERN_SUFFIXES = {
        '-chi': re.compile(r'(\d+)-chi\b', re.IGNORECASE),
        '-son': re.compile(r'(\d+)-son\b', re.IGNORECASE),
        '-raqam': re.compile(r'(\d+)-raqam\b', re.IGNORECASE),
        '-band': re.compile(r'(\d+)-band\b', re.IGNORECASE),
        '-modda': re.compile(r'(\d+)-modda\b', re.IGNORECASE),
        '-bob': re.compile(r'(\d+)-bob\b', re.IGNORECASE),
        '-qism': re.compile(r'(\d+)-qism\b', re.IGNORECASE),
        "-bo'lim": re.compile(r"(\d+)-bo'lim\b", re.IGNORECASE),
        '-punkt': re.compile(r'(\d+)-punkt\b', re.IGNORECASE),
        '-jadval': re.compile(r'(\d+)-jadval\b', re.IGNORECASE),
        '-rasm': re.compile(r'(\d+)-rasm\b', re.IGNORECASE),
        '-misol': re.compile(r'(\d+)-misol\b', re.IGNORECASE),
        '-ilova': re.compile(r'(\d+)-ilova\b', re.IGNORECASE),
    }

    # ========================================
    # ORDINAL WITH WORD PATTERNS
    # ========================================

    # Known suffixes to exclude from generic ordinal-word pattern
    _KNOWN_SUFFIXES = frozenset([
        'chi', 'son', 'raqam', 'band', 'modda', 'bob', 'qism',
        "bo'lim", 'punkt', 'jadval', 'rasm', 'misol', 'ilova',
        'inchi', 'nchi'  # ordinal suffixes
    ])

    # Pattern for number-word: 1-uy -> birinchi uy
    # Matches: digit(s) + hyphen + word (not known suffixes)
    _PATTERN_ORDINAL_WORD = re.compile(r'(\d+)-([a-zA-Z\']+)\b', re.UNICODE)

    # Pattern for number. word: 1. uy -> birinchidan, uy
    # Matches: digit(s) + dot + space(s) + word
    _PATTERN_ORDINAL_DOT_WORD = re.compile(r'(\d+)\.\s+([a-zA-Z\']+)\b', re.UNICODE)

    # ========================================
    # PARENTHESES PATTERNS
    # ========================================

    # Opening parenthesis: ( -> qavs ichida
    _PATTERN_PAREN_OPEN = re.compile(r'\(')
    # Closing parenthesis: ) -> qavs yopilgan
    _PATTERN_PAREN_CLOSE = re.compile(r'\)')

    # ========================================
    # CURRENCY SYMBOL PATTERNS
    # ========================================

    # Dollar patterns: $100, $ 100, 100$, 100 $
    _PATTERN_DOLLAR_BEFORE = re.compile(r'\$\s*(\d+(?:[.,]\d+)?)')  # $100, $ 100
    _PATTERN_DOLLAR_AFTER = re.compile(r'(\d+(?:[.,]\d+)?)\s*\$')   # 100$, 100 $

    # ========================================
    # SPECIAL SYMBOLS
    # ========================================

    # @ symbol -> kuchukcha
    _PATTERN_AT = re.compile(r'@')

    # ========================================
    # EMAIL PATTERNS
    # ========================================

    # Email pattern: user@domain.com
    _PATTERN_EMAIL = re.compile(
        r'\b([a-zA-Z0-9._%+-]+)@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\b',
        re.UNICODE
    )

    # Known domain/TLD pronunciations
    _DOMAIN_PRONUNCIATIONS = {
        # Email providers
        'gmail': 'jimayl',
        'mail': 'meyl',
        'email': 'imeyl',
        'yahoo': 'yaxu',
        'hotmail': 'xotmeyl',
        'outlook': 'autluk',
        'yandex': 'yandeks',
        'proton': 'proton',
        'icloud': 'ayklaud',
        'company': 'kompeniy',
        'user': 'yuzer',
        'users': 'yuzerz',
        'startup': 'startap',
        'example': 'egzempl',
        'test': 'test',
        'admin': 'admin',
        'info': 'info',
        'support': 'sapport',
        'contact': 'kontakt',
        'service': 'servis',
        'online': 'onlayn',
        'cloud': 'klaud',
        'tech': 'tek',
        'digital': 'dijital',
        'media': 'mediya',
        'shop': 'shop',
        'store': 'stor',
        'news': 'nyuz',
        'blog': 'blog',
        'site': 'sayt',
        'web': 'veb',
        'app': 'epp',
        'mobile': 'mobayl',
        'global': 'global',
        'world': 'vorld',
        'group': 'grup',
        'team': 'tim',
        'dev': 'dev',
        'code': 'kod',
        'data': 'deyta',
        'host': 'xost',
        'server': 'server',
        'live': 'layv',
        'pro': 'pro',
        'plus': 'plyas',
        'express': 'ekspress',
        # TLDs
        'com': 'kom',
        'net': 'net',
        'org': 'org',
        'ru': 'ru',
        'uz': 'uz',
        'info': 'info',
        'edu': 'edu',
        'gov': 'gov',
        'io': 'ayou',
        'co': 'ko',
    }

    def __init__(self, number_converter: "UzNumberToWords"):
        """
        Initialize text preprocessor.
        
        Args:
            number_converter: Instance of UzNumberToWords for number conversion
        """
        self.n = number_converter
    
    def _replace_with_ordinal(self, text: str, pattern: re.Pattern) -> str:
        """
        Replace matched numbers with ordinal form.

        Args:
            text: Input text
            pattern: Compiled regex pattern

        Returns:
            Text with replacements
        """
        def replacer(match):
            number_str = match.group(1)
            try:
                number = int(number_str)
                return self.n.ordinal(number)
            except (ValueError, AttributeError):
                return match.group(0)

        return pattern.sub(replacer, text)

    def _replace_with_raqami(self, text: str, pattern: re.Pattern) -> str:
        """
        Replace matched numbers with "raqami" + cardinal form.

        Args:
            text: Input text
            pattern: Compiled regex pattern

        Returns:
            Text with replacements (e.g., "№12" -> "raqami o'n ikki")
        """
        def replacer(match):
            number_str = match.group(1)
            try:
                number = int(number_str)
                cardinal = self.n.number(number)
                return f"raqami {cardinal}"
            except (ValueError, AttributeError):
                return match.group(0)

        return pattern.sub(replacer, text)
    
    def _replace_markers(self, text: str) -> str:
        """
        Replace numbers in markers with ordinal form.
        Markers themselves remain unchanged.
        
        Args:
            text: Input text
            
        Returns:
            Text with marker number replacements
        """
        result = text
        
        for marker, pattern in self._PATTERN_MARKERS.items():
            # Capture marker for closure
            current_marker = marker
            
            def make_replacer(m):
                def replacer(match):
                    number_str = match.group(1)
                    try:
                        number = int(number_str)
                        ordinal = self.n.ordinal(number)
                        return f"{m} {ordinal}"
                    except (ValueError, AttributeError):
                        return match.group(0)
                return replacer
            
            result = pattern.sub(make_replacer(current_marker), result)
        
        return result
    
    def _replace_suffixes(self, text: str) -> str:
        """
        Replace number-suffix patterns with ordinal form.

        Args:
            text: Input text

        Returns:
            Text with suffix replacements
        """
        result = text

        for suffix, pattern in self._PATTERN_SUFFIXES.items():
            current_suffix = suffix

            def make_replacer(s):
                def replacer(match):
                    number_str = match.group(1)
                    try:
                        number = int(number_str)
                        ordinal = self.n.ordinal(number)
                        # For -chi suffix, just return ordinal (chi is already ordinal)
                        if s == '-chi':
                            return ordinal
                        # For other suffixes, add space: "birinchi bob" not "birinchi-bob"
                        return f"{ordinal} {s[1:]}"  # Remove leading hyphen
                    except (ValueError, AttributeError):
                        return match.group(0)
                return replacer

            result = pattern.sub(make_replacer(current_suffix), result)

        return result

    def _replace_ordinal_word(self, text: str) -> str:
        """
        Replace number-word patterns with ordinal + word.

        Converts patterns like "1-uy" to "birinchi uy".
        Excludes known suffixes (chi, son, bob, etc.).

        Args:
            text: Input text

        Returns:
            Text with ordinal-word replacements
        """
        def replacer(match):
            number_str = match.group(1)
            word = match.group(2)

            # Skip known suffixes - they are handled by _replace_suffixes
            if word.lower() in self._KNOWN_SUFFIXES:
                return match.group(0)

            try:
                number = int(number_str)
                ordinal = self.n.ordinal(number)
                return f"{ordinal} {word}"
            except (ValueError, AttributeError):
                return match.group(0)

        return self._PATTERN_ORDINAL_WORD.sub(replacer, text)

    def _replace_ordinal_dot_word(self, text: str) -> str:
        """
        Replace number. word patterns with ordinal-dan, word.

        Converts patterns like "1. uy" to "birinchidan, uy".

        Args:
            text: Input text

        Returns:
            Text with ordinal-dan replacements
        """
        def replacer(match):
            number_str = match.group(1)
            word = match.group(2)

            try:
                number = int(number_str)
                ordinal = self.n.ordinal(number)
                # Add "dan" suffix: birinchi -> birinchidan
                return f"{ordinal}dan, {word}"
            except (ValueError, AttributeError):
                return match.group(0)

        return self._PATTERN_ORDINAL_DOT_WORD.sub(replacer, text)

    def _replace_parentheses(self, text: str) -> str:
        """
        Replace parentheses with Uzbek words.

        Converts:
        - "(" -> " qavs ichida "
        - ")" -> " qavs yopilgan "

        Args:
            text: Input text

        Returns:
            Text with parentheses replaced
        """
        result = self._PATTERN_PAREN_OPEN.sub(' qavs ichida ', text)
        result = self._PATTERN_PAREN_CLOSE.sub(' qavs yopilgan ', result)
        # Clean up multiple spaces
        result = re.sub(r' +', ' ', result)
        return result.strip()

    def _replace_dollar(self, text: str) -> str:
        """
        Replace dollar currency patterns with Uzbek words.

        Converts:
        - "$100" -> "yuz dollar"
        - "$ 100" -> "yuz dollar"
        - "100$" -> "yuz dollar"
        - "100 $" -> "yuz dollar"

        Args:
            text: Input text

        Returns:
            Text with dollar amounts converted
        """
        def replacer(match):
            number_str = match.group(1)
            try:
                # Normalize number
                clean = number_str.replace(",", ".")
                cardinal = self.n.number(clean)
                return f"{cardinal} dollar"
            except (ValueError, AttributeError):
                return match.group(0)

        # Replace $ before number ($100, $ 100)
        result = self._PATTERN_DOLLAR_BEFORE.sub(replacer, text)
        # Replace $ after number (100$, 100 $)
        result = self._PATTERN_DOLLAR_AFTER.sub(replacer, result)
        return result

    def _replace_at_symbol(self, text: str) -> str:
        """
        Replace @ symbol with Uzbek word.

        Converts: @ -> kuchukcha

        Args:
            text: Input text

        Returns:
            Text with @ replaced
        """
        return self._PATTERN_AT.sub(' kuchukcha ', text)

    def _replace_email(self, text: str) -> str:
        """
        Replace email addresses with Uzbek pronunciation.

        Converts: javharbek@gmail.com -> javharbek kuchukcha jimayl nuqta kom

        Args:
            text: Input text

        Returns:
            Text with emails converted
        """
        def replacer(match):
            username = match.group(1)
            domain = match.group(2)

            # Split domain into parts
            domain_parts = domain.lower().split('.')

            # Convert each part
            converted_parts = []
            for part in domain_parts:
                # Check if we have a known pronunciation
                if part in self._DOMAIN_PRONUNCIATIONS:
                    converted_parts.append(self._DOMAIN_PRONUNCIATIONS[part])
                else:
                    converted_parts.append(part)

            # Join with "nuqta" (dot)
            domain_converted = ' nuqta '.join(converted_parts)

            return f"{username} kuchukcha {domain_converted}"

        return self._PATTERN_EMAIL.sub(replacer, text)
    
    def process(
        self,
        text: str,
        convert_numbers: bool = True,
        convert_markers: bool = True,
        convert_suffixes: bool = True,
        convert_ordinal_words: bool = True,
        convert_parentheses: bool = True,
        convert_dollar: bool = True,
        convert_email: bool = True,
        convert_at_symbol: bool = True
    ) -> str:
        """
        Process text to convert number markers to words.

        Args:
            text: Input text to process
            convert_numbers: If True, convert № and # markers
            convert_markers: If True, convert Latin markers (No., p., art., etc.)
            convert_suffixes: If True, convert Uzbek suffixes (-chi, -son, etc.)
            convert_ordinal_words: If True, convert ordinal-word patterns (1-uy, 1. uy)
            convert_parentheses: If True, convert ( ) to "qavs ichida/yopilgan"
            convert_dollar: If True, convert $100, 100$ to "yuz dollar"
            convert_email: If True, convert emails like user@gmail.com
            convert_at_symbol: If True, convert standalone @ to "kuchukcha"

        Returns:
            Processed text with numbers converted to words

        Example:
            >>> preprocessor.process("javharbek@gmail.com")
            'javharbek kuchukcha jimayl nuqta kom'
            >>> preprocessor.process("$100")
            'yuz dollar'
        """
        result = text

        # Email should be processed BEFORE at_symbol to handle emails as a unit
        if convert_email:
            result = self._replace_email(result)

        # Dollar should be processed early to avoid conflicts with numbers
        if convert_dollar:
            result = self._replace_dollar(result)

        if convert_numbers:
            # Replace № before number (№1, № 1) with "raqami"
            result = self._replace_with_raqami(result, self._PATTERN_NUM_BEFORE)

            # Replace № after number (1№, 1 №) with "raqami"
            result = self._replace_with_raqami(result, self._PATTERN_NUM_AFTER)

            # Replace # before number (#1, # 1) with ordinal
            result = self._replace_with_ordinal(result, self._PATTERN_HASH_BEFORE)

            # Replace # after number (1#, 1 #) with ordinal
            result = self._replace_with_ordinal(result, self._PATTERN_HASH_AFTER)

        if convert_markers:
            result = self._replace_markers(result)

        if convert_suffixes:
            result = self._replace_suffixes(result)

        if convert_ordinal_words:
            # Replace number-word patterns (1-uy -> birinchi uy)
            # Must be after convert_suffixes to avoid conflicts
            result = self._replace_ordinal_word(result)
            # Replace number. word patterns (1. uy -> birinchidan, uy)
            result = self._replace_ordinal_dot_word(result)

        if convert_parentheses:
            result = self._replace_parentheses(result)

        if convert_at_symbol:
            result = self._replace_at_symbol(result)

        return result
    
    def process_file(
        self, 
        input_path: str, 
        output_path: str = None,
        convert_numbers: bool = True, 
        convert_markers: bool = True,
        convert_suffixes: bool = True,
        encoding: str = 'utf-8'
    ) -> str:
        """
        Process a text file and save the result.
        
        Args:
            input_path: Path to input file
            output_path: Path to output file (if None, overwrites input)
            convert_numbers: If True, convert № and # markers
            convert_markers: If True, convert Latin markers
            convert_suffixes: If True, convert Uzbek suffixes
            encoding: File encoding (default: utf-8)
            
        Returns:
            Processed text content
            
        Example:
            >>> preprocessor.process_file("document.txt", "document_processed.txt")
        """
        with open(input_path, 'r', encoding=encoding) as f:
            content = f.read()
        
        processed = self.process(
            content, 
            convert_numbers, 
            convert_markers, 
            convert_suffixes
        )
        
        output = output_path if output_path else input_path
        with open(output, 'w', encoding=encoding) as f:
            f.write(processed)
        
        return processed
