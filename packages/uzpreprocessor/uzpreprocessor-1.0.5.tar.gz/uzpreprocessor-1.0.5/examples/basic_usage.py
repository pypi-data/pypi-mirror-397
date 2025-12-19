#!/usr/bin/env python3
"""
Basic usage examples for UzPreprocessor library.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

from uzpreprocessor import UzPreprocessor, ProcessingConfig

def main():
    """Run basic usage examples."""
    
    # Initialize the processor
    processor = UzPreprocessor()
    
    print("=" * 60)
    print("UzPreprocessor - Basic Usage Examples")
    print("=" * 60)
    print()
    
    # Number conversion
    print("1. NUMBER CONVERSION")
    print("-" * 60)
    print(f"123 -> {processor.number.number(123)}")
    print(f"123.456 -> {processor.number.number(123.456)}")
    print(f"-42 -> {processor.number.number(-42)}")
    print(f"5 (ordinal) -> {processor.number.ordinal(5)}")
    print()
    
    # Currency conversion
    print("2. CURRENCY CONVERSION")
    print("-" * 60)
    print(f"1000 -> {processor.number.money(1000)}")
    print(f"12345.67 -> {processor.number.money(12345.67)}")
    print()
    
    # Percentage conversion
    print("3. PERCENTAGE CONVERSION")
    print("-" * 60)
    print(f"12.345 -> {processor.number.percent(12.345)}")
    print()
    
    # Date conversion
    print("4. DATE CONVERSION")
    print("-" * 60)
    print(f"2025-09-18 -> {processor.date.date('2025-09-18')}")
    print(f"18.09.2025 -> {processor.date.date('18.09.2025')}")
    print(f"18 September 2025 -> {processor.date.date('18 September 2025')}")
    print()
    
    # Time conversion
    print("5. TIME CONVERSION")
    print("-" * 60)
    print(f"14:35:08 -> {processor.time.time('14:35:08')}")
    print(f"2 PM -> {processor.time.time('2 PM')}")
    print()
    
    # DateTime conversion
    print("6. DATETIME CONVERSION")
    print("-" * 60)
    print(f"2025-09-18T14:35:08 -> {processor.datetime.datetime('2025-09-18T14:35:08')}")
    print()
    
    # Text preprocessing (markers only)
    print("7. TEXT MARKER PREPROCESSING")
    print("-" * 60)
    test1 = processor.text.process("Bu No.1 va #2")
    print(f"Bu No.1 va #2 -> {test1}")
    test2 = processor.text.process("1-bob, 2-modda")
    print(f"1-bob, 2-modda -> {test2}")
    print()
    
    # MAIN FEATURE: Full automatic text processing
    print("=" * 60)
    print("8. AUTOMATIC TEXT PROCESSING (process method)")
    print("=" * 60)
    print()
    
    sample_text = """Shartnoma No.123
Sana: 2025-09-18, soat 14:35
Summa: 12500 so'm (15% chegirma bilan)
Art.5, p.3 asosida, 1-bob, 2-modda

Jadval #45:
- 1-chi element: 100 dona
- 2-chi element: 250 dona
- 3-chi element: 375 dona

Jami: 15750 so'm"""

    print("ORIGINAL TEXT:")
    print("-" * 60)
    print(sample_text)
    print()
    
    print("PROCESSED TEXT:")
    print("-" * 60)
    processed = processor.process(sample_text)
    print(processed)
    print()
    
    # Analysis feature
    print("TEXT ANALYSIS:")
    print("-" * 60)
    analysis = processor.analyze(sample_text)
    print(f"Total tokens found: {analysis['total_tokens']}")
    print(f"By type: {analysis['type_counts']}")
    print()
    
    # Selective processing
    print("9. SELECTIVE PROCESSING")
    print("-" * 60)
    
    text = "2025-09-18 14:35 12500"
    print(f"Original: {text}")
    print(f"Numbers only: {processor.numbers_only(text)}")
    print(f"Dates only: {processor.dates_only(text)}")
    print(f"Times only: {processor.times_only(text)}")
    print()
    
    # Custom configuration
    print("10. CUSTOM CONFIGURATION")
    print("-" * 60)
    
    config = ProcessingConfig(
        process_numbers=True,
        process_dates=False,
        process_times=False,
        process_money=True,
        preserve_original=True  # Keep original in parentheses
    )
    
    text = "Narx: 12500 so'm, sana: 2025-09-18"
    custom_processor = UzPreprocessor(config)
    print(f"Original: {text}")
    print(f"With preserve_original=True: {custom_processor.process(text)}")
    print()
    
    print("=" * 60)
    print("All examples completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
