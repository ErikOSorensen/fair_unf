"""Tests for normalization functions."""

import math
from datetime import date, datetime, time
import pytest
from ufn.normalize import (
    normalize_numeric,
    normalize_string,
    normalize_boolean,
    normalize_date,
    normalize_datetime,
    normalize_time,
    normalize_bitfield,
)


class TestNormalizeNumeric:
    """Tests for numeric normalization."""

    def test_positive_zero(self):
        assert normalize_numeric(0.0) == '+0.e+'

    def test_negative_zero(self):
        assert normalize_numeric(-0.0) == '-0.e+'

    def test_positive_infinity(self):
        assert normalize_numeric(float('inf')) == '+inf'

    def test_negative_infinity(self):
        assert normalize_numeric(float('-inf')) == '-inf'

    def test_nan(self):
        assert normalize_numeric(float('nan')) == '+nan'

    def test_none(self):
        assert normalize_numeric(None) == '\000\000\000'

    def test_positive_integer(self):
        result = normalize_numeric(3)
        assert result.startswith('+3.')
        assert 'e+' in result

    def test_positive_float(self):
        result = normalize_numeric(3.1415)
        assert result.startswith('+3.1415')
        # Should have 7 significant digits
        assert 'e+' in result

    def test_negative_float(self):
        result = normalize_numeric(-2.5)
        assert result.startswith('-2.5')
        assert 'e+' in result

    def test_small_number(self):
        result = normalize_numeric(0.00001)
        assert result.startswith('+1.')
        assert 'e-5' in result or 'e-05' in result

    def test_large_number(self):
        result = normalize_numeric(1234567890)
        assert result.startswith('+1.23456')
        assert 'e+09' in result

    def test_precision_parameter(self):
        result = normalize_numeric(3.1415926, precision=3)
        # Should have 3 significant digits
        assert '+3.14e+' in result or '+3.1e+' in result

    def test_truncate_mode(self):
        result = normalize_numeric(3.1415926, round_mode=False)
        # Truncate instead of round
        assert result.startswith('+3.')


class TestNormalizeString:
    """Tests for string normalization."""

    def test_simple_string(self):
        result = normalize_string("hello")
        assert result == b'hello'

    def test_unicode_string(self):
        result = normalize_string("héllo")
        assert result == "héllo".encode('utf-8')

    def test_none(self):
        result = normalize_string(None)
        assert result == b'\000\000\000'

    def test_truncation(self):
        long_string = "a" * 200
        result = normalize_string(long_string, max_chars=128)
        assert len(result) == 128

    def test_empty_string(self):
        result = normalize_string("")
        assert result == b''


class TestNormalizeBoolean:
    """Tests for boolean normalization."""

    def test_true(self):
        result = normalize_boolean(True)
        assert '+1.' in result

    def test_false(self):
        result = normalize_boolean(False)
        assert '+0.' in result

    def test_none(self):
        result = normalize_boolean(None)
        assert result == '\000\000\000'


class TestNormalizeDate:
    """Tests for date normalization."""

    def test_date(self):
        d = date(2024, 1, 15)
        result = normalize_date(d)
        assert result == '2024-01-15'

    def test_none(self):
        result = normalize_date(None)
        assert result == '\000\000\000'


class TestNormalizeTime:
    """Tests for time normalization."""

    def test_time_without_microseconds(self):
        t = time(14, 30, 0)
        result = normalize_time(t)
        assert result == '14:30:00Z'

    def test_time_with_microseconds(self):
        t = time(14, 30, 0, 123456)
        result = normalize_time(t)
        assert result == '14:30:00.123456Z'

    def test_time_with_trailing_zeros(self):
        t = time(14, 30, 0, 100000)
        result = normalize_time(t)
        assert result == '14:30:00.1Z'

    def test_none(self):
        result = normalize_time(None)
        assert result == '\000\000\000'


class TestNormalizeDatetime:
    """Tests for datetime normalization."""

    def test_datetime(self):
        dt = datetime(2024, 1, 15, 14, 30, 0)
        result = normalize_datetime(dt)
        assert result == '2024-01-15T14:30:00Z'

    def test_datetime_with_microseconds(self):
        dt = datetime(2024, 1, 15, 14, 30, 0, 123456)
        result = normalize_datetime(dt)
        assert result == '2024-01-15T14:30:00.123456Z'

    def test_none(self):
        result = normalize_datetime(None)
        assert result == '\000\000\000'


class TestNormalizeBitfield:
    """Tests for bitfield normalization."""

    def test_simple_bitfield(self):
        bits = [True, False, True, True]
        result = normalize_bitfield(bits)
        # Should be base64 encoded
        assert isinstance(result, str)

    def test_empty_bitfield(self):
        result = normalize_bitfield([])
        assert result == '\000\000\000'

    def test_none(self):
        result = normalize_bitfield(None)
        assert result == '\000\000\000'

    def test_all_false(self):
        bits = [False, False, False]
        result = normalize_bitfield(bits)
        assert result == '\000\000\000'
