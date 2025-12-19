"""Tests for gss package."""

import pandas as pd
import pytest

import gss


class TestVariables:
    """Tests for gss.variables()."""

    def test_returns_list(self):
        """variables() returns a list."""
        result = gss.variables()
        assert isinstance(result, list)

    def test_contains_known_variables(self):
        """variables() includes known GSS variables."""
        result = gss.variables()
        assert "HOMOSEX" in result
        assert "GRASS" in result
        assert "TRUST" in result

    def test_all_uppercase(self):
        """All variable names are uppercase."""
        result = gss.variables()
        for var in result:
            assert var == var.upper()


class TestInfo:
    """Tests for gss.info()."""

    def test_returns_dict(self):
        """info() returns a dictionary."""
        result = gss.info("HOMOSEX")
        assert isinstance(result, dict)

    def test_has_required_keys(self):
        """info() result has required keys."""
        result = gss.info("HOMOSEX")
        assert "question" in result
        assert "responses" in result
        assert "first_year" in result
        assert "description" in result

    def test_question_is_string(self):
        """Question text is a non-empty string."""
        result = gss.info("HOMOSEX")
        assert isinstance(result["question"], str)
        assert len(result["question"]) > 10

    def test_responses_is_dict(self):
        """Responses is a dictionary mapping codes to labels."""
        result = gss.info("HOMOSEX")
        assert isinstance(result["responses"], dict)
        assert len(result["responses"]) > 0

    def test_first_year_is_int(self):
        """First year is an integer in valid range."""
        result = gss.info("HOMOSEX")
        assert isinstance(result["first_year"], int)
        assert 1972 <= result["first_year"] <= 2000

    def test_unknown_variable_raises(self):
        """info() raises KeyError for unknown variable."""
        with pytest.raises(KeyError):
            gss.info("NOT_A_VARIABLE")

    def test_case_insensitive(self):
        """info() accepts lowercase variable names."""
        result = gss.info("homosex")
        assert "question" in result


class TestTrend:
    """Tests for gss.trend()."""

    def test_returns_dataframe(self):
        """trend() returns a pandas DataFrame."""
        result = gss.trend("HOMOSEX")
        assert isinstance(result, pd.DataFrame)

    def test_has_required_columns(self):
        """trend() result has year and pct columns."""
        result = gss.trend("HOMOSEX")
        assert "year" in result.columns
        assert "pct" in result.columns

    def test_years_are_sorted(self):
        """Years are in ascending order."""
        result = gss.trend("HOMOSEX")
        years = result["year"].tolist()
        assert years == sorted(years)

    def test_pct_in_valid_range(self):
        """Percentages are between 0 and 100."""
        result = gss.trend("HOMOSEX")
        assert (result["pct"] >= 0).all()
        assert (result["pct"] <= 100).all()

    def test_has_multiple_years(self):
        """trend() returns data for multiple years."""
        result = gss.trend("HOMOSEX")
        assert len(result) >= 20  # GSS has been running since 1972

    def test_unknown_variable_raises(self):
        """trend() raises KeyError for unknown variable."""
        with pytest.raises(KeyError):
            gss.trend("NOT_A_VARIABLE")

    def test_case_insensitive(self):
        """trend() accepts lowercase variable names."""
        result = gss.trend("homosex")
        assert len(result) > 0

    def test_homosex_trend_increases(self):
        """HOMOSEX acceptance has increased over time (sanity check)."""
        result = gss.trend("HOMOSEX")
        early = result[result["year"] <= 1990]["pct"].mean()
        late = result[result["year"] >= 2010]["pct"].mean()
        assert late > early  # Acceptance has increased


class TestTrendWithResponse:
    """Tests for gss.trend() with specific response."""

    def test_liberal_response_default(self):
        """Default returns liberal/progressive response percentage."""
        result = gss.trend("HOMOSEX")
        # By default should track "not wrong at all"
        assert result[result["year"] == 2022]["pct"].iloc[0] == 61


class TestIntegration:
    """Integration tests."""

    def test_all_variables_have_info(self):
        """All variables returned by variables() have valid info()."""
        for var in gss.variables():
            info = gss.info(var)
            assert "question" in info
            assert "responses" in info

    def test_all_variables_have_trends(self):
        """All variables returned by variables() have valid trend()."""
        for var in gss.variables():
            trend = gss.trend(var)
            assert len(trend) > 0
            assert "year" in trend.columns
            assert "pct" in trend.columns
