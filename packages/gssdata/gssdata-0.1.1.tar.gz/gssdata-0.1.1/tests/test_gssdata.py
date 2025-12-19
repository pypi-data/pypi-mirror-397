"""Tests for gssdata package."""

import pandas as pd
import pytest

import gssdata


class TestVariables:
    """Tests for gssdata.variables()."""

    def test_returns_list(self):
        """variables() returns a list."""
        result = gssdata.variables()
        assert isinstance(result, list)

    def test_contains_known_variables(self):
        """variables() includes known GSS variables."""
        result = gssdata.variables()
        assert "HOMOSEX" in result
        assert "GRASS" in result
        assert "TRUST" in result

    def test_all_uppercase(self):
        """All variable names are uppercase."""
        result = gssdata.variables()
        for var in result:
            assert var == var.upper()


class TestInfo:
    """Tests for gssdata.info()."""

    def test_returns_dict(self):
        """info() returns a dictionary."""
        result = gssdata.info("HOMOSEX")
        assert isinstance(result, dict)

    def test_has_required_keys(self):
        """info() result has required keys."""
        result = gssdata.info("HOMOSEX")
        assert "question" in result
        assert "responses" in result
        assert "first_year" in result
        assert "description" in result

    def test_question_is_string(self):
        """Question text is a non-empty string."""
        result = gssdata.info("HOMOSEX")
        assert isinstance(result["question"], str)
        assert len(result["question"]) > 10

    def test_responses_is_dict(self):
        """Responses is a dictionary mapping codes to labels."""
        result = gssdata.info("HOMOSEX")
        assert isinstance(result["responses"], dict)
        assert len(result["responses"]) > 0

    def test_first_year_is_int(self):
        """First year is an integer in valid range."""
        result = gssdata.info("HOMOSEX")
        assert isinstance(result["first_year"], int)
        assert 1972 <= result["first_year"] <= 2000

    def test_unknown_variable_raises(self):
        """info() raises KeyError for unknown variable."""
        with pytest.raises(KeyError):
            gssdata.info("NOT_A_VARIABLE")

    def test_case_insensitive(self):
        """info() accepts lowercase variable names."""
        result = gssdata.info("homosex")
        assert "question" in result


class TestTrend:
    """Tests for gssdata.trend()."""

    def test_returns_dataframe(self):
        """trend() returns a pandas DataFrame."""
        result = gssdata.trend("HOMOSEX")
        assert isinstance(result, pd.DataFrame)

    def test_has_required_columns(self):
        """trend() result has year and pct columns."""
        result = gssdata.trend("HOMOSEX")
        assert "year" in result.columns
        assert "pct" in result.columns

    def test_years_are_sorted(self):
        """Years are in ascending order."""
        result = gssdata.trend("HOMOSEX")
        years = result["year"].tolist()
        assert years == sorted(years)

    def test_pct_in_valid_range(self):
        """Percentages are between 0 and 100."""
        result = gssdata.trend("HOMOSEX")
        assert (result["pct"] >= 0).all()
        assert (result["pct"] <= 100).all()

    def test_has_multiple_years(self):
        """trend() returns data for multiple years."""
        result = gssdata.trend("HOMOSEX")
        assert len(result) >= 20  # GSS has been running since 1972

    def test_unknown_variable_raises(self):
        """trend() raises KeyError for unknown variable."""
        with pytest.raises(KeyError):
            gssdata.trend("NOT_A_VARIABLE")

    def test_case_insensitive(self):
        """trend() accepts lowercase variable names."""
        result = gssdata.trend("homosex")
        assert len(result) > 0

    def test_homosex_trend_increases(self):
        """HOMOSEX acceptance has increased over time (sanity check)."""
        result = gssdata.trend("HOMOSEX")
        early = result[result["year"] <= 1990]["pct"].mean()
        late = result[result["year"] >= 2010]["pct"].mean()
        assert late > early  # Acceptance has increased


class TestTrendWithResponse:
    """Tests for gssdata.trend() with specific response."""

    def test_liberal_response_default(self):
        """Default returns liberal/progressive response percentage."""
        result = gssdata.trend("HOMOSEX")
        # By default should track "not wrong at all"
        assert result[result["year"] == 2022]["pct"].iloc[0] == 61


class TestIntegration:
    """Integration tests."""

    def test_all_variables_have_info(self):
        """All variables returned by variables() have valid info()."""
        for var in gssdata.variables():
            info = gssdata.info(var)
            assert "question" in info
            assert "responses" in info

    def test_all_variables_have_trends(self):
        """All variables returned by variables() have valid trend()."""
        for var in gssdata.variables():
            trend = gssdata.trend(var)
            assert len(trend) > 0
            assert "year" in trend.columns
            assert "pct" in trend.columns
