

import logging
import unittest

from glasswall.config.logging import format_object, log, log_handler


class TestLoggingConfiguration(unittest.TestCase):
    # Define messages with non-ASCII characters from different encodings
    messages = [
        ("utf-8", "プリンセスメーカー2_b.FDI"),  # Japanese characters
        ("utf-8", "αβγδ"),  # Greek characters
        ("cp1252", "©®"),  # Copyright and Registered symbols
        ("utf-8", "𐍆"),  # Ancient Greek character
        ("utf-8", "你好"),  # Chinese characters
        ("utf-8", "Привет"),  # Russian characters
        ("utf-8", "こんにちは"),  # Japanese characters
        ("utf-8", "مرحبا"),  # Arabic characters
        ("utf-8", "नमस्ते"),  # Hindi characters
        ("utf-8", "안녕하세요"),  # Korean characters
        ("utf-8", "Γεια σας"),  # Greek characters
        ("utf-8", "שלום"),  # Hebrew characters
        ("utf-8", "Hola"),  # Spanish characters
        ("utf-8", "Bonjour"),  # French characters
        ("utf-8", "Ciao"),  # Italian characters
        ("utf-8", "Olá"),  # Portuguese characters
        ("utf-8", "こんにちは"),  # Japanese characters
        ("utf-8", "Привет"),  # Russian characters
        ("utf-8", "你好"),  # Chinese characters
        ("utf-8", "مرحبا"),  # Arabic characters
        ("utf-8", "नमस्ते"),  # Hindi characters
        ("utf-8", "안녕하세요"),  # Korean characters
        ("utf-8", "Γεια σας"),  # Greek characters
        ("utf-8", "שלום"),  # Hebrew characters
        ("utf-8", "Hola"),  # Spanish characters
        ("utf-8", "Bonjour"),  # French characters
        ("utf-8", "Ciao"),  # Italian characters
        ("utf-8", "Olá"),  # Portuguese characters
        ("iso-8859-1", "áéíóú"),  # Latin-1 characters
        ("utf-16", "😀😎🤩"),  # Emojis
        ("utf-8", "東京"),  # Japanese city name
        ("iso-8859-7", "καλημέρα"),  # Greek greeting
    ]

    def test_format_object(self):
        """
        Test the format_object function to ensure it correctly formats an object's attributes.
        This test creates a simple TestObject with two attributes and checks if the format_object
        function returns the expected string representation of the object's attributes.
        """
        # Define a simple class with two attributes for testing
        class TestObject:
            def __init__(self):
                self.attr1 = "value1"
                self.attr2 = "value2"

        # Create an instance of TestObject
        obj = TestObject()
        # Call the format_object function with the TestObject instance
        formatted = format_object(obj)
        # Assert that the formatted string matches the expected output
        self.assertEqual(formatted, "\n\tattr1: value1\n\tattr2: value2")

    def test_log_levels(self):
        """
        Test that logging messages are correctly logged at different log levels.
        This test iterates over a list of log levels and messages, logs each message at the
        corresponding log level, and checks if the expected log message is captured.
        """
        # Define log levels and corresponding messages
        log_levels = [
            (logging.DEBUG, "Debug message"),
            (logging.INFO, "Info message"),
            (logging.WARNING, "Warning message"),
            (logging.ERROR, "Error message"),
            (logging.CRITICAL, "Critical message")
        ]

        # Iterate over log levels and test each one
        for level, message in log_levels:
            with self.subTest(level=logging.getLevelName(level)):
                # Use assertLogs to capture log messages for the current level
                with self.assertLogs(log, level=level) as cm:
                    log.log(level, message)

                # Construct the expected log message format
                expected_log_message = f"{logging.getLevelName(level)}:glasswall.config.logging:{message}"
                # Assert that the expected log message is in the captured output
                self.assertIn(expected_log_message, cm.output)

    def test_logging_non_ascii_characters_to_console(self):
        """
        Test that non-ASCII characters are correctly logged to the console.
        This test iterates over a list of messages with different encodings
        and logs each message to the console. It then checks if the expected
        log message is present in the captured console output.
        """
        for encoding, message in self.messages:
            with self.subTest(encoding=encoding, message=message):
                # Use assertLogs to capture log messages for the current encoding
                with self.assertLogs(log, level=logging.INFO) as cm:
                    log.info(message)
                # Construct the expected log message format
                expected_log_message = f"INFO:glasswall.config.logging:{message}"
                # Assert that the expected log message is in the captured output
                self.assertIn(expected_log_message, cm.output)

    def test_logging_non_ascii_characters_to_file(self):
        """
        Test that non-ASCII characters are correctly logged to a file.
        This test iterates over a list of messages with different encodings
        and logs each message to a file. It then reads the log file and checks
        if the expected message is present in the file contents.
        """
        for encoding, message in self.messages:
            with self.subTest(encoding=encoding, message=message):
                # Log the message to the file
                log.info(message)

                # Read the contents of the log file
                with open(log_handler.baseFilename, "r", encoding="utf-8") as f:
                    log_contents = f.read()

                # Assert that the expected message is in the log file contents
                self.assertIn(message, log_contents)


if __name__ == "__main__":
    unittest.main()
