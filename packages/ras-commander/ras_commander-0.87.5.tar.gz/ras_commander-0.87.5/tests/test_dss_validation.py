"""
Test Suite for DSS Validation (Integrated API)

Tests the new integrated validation API in RasDss class.
Uses real HEC-RAS example projects (following ras-commander testing philosophy).

Test coverage:
- DSS pathname format validation (check_pathname_format, is_valid_pathname)
- File existence checking (check_file_exists)
- Pathname existence in catalog (check_pathname_exists)
- Data availability validation (check_data_availability)
- Combined validation (check_pathname, is_pathname_available)

Uses BaldEagleCrkMulti2D example project which has DSS boundary conditions.
"""

import pytest
from pathlib import Path
from datetime import datetime

# Try importing validation classes
try:
    from ras_commander.dss import RasDss
    from ras_commander.validation_base import ValidationSeverity, ValidationResult, ValidationReport
    RASDSS_AVAILABLE = True
except ImportError:
    RASDSS_AVAILABLE = False
    pytest.skip("RasDss or validation_base not available", allow_module_level=True)


class TestPathnameFormatValidation:
    """Test DSS pathname format validation"""

    def test_valid_format(self):
        """Test valid DSS pathname format"""
        pathname = "//BASIN/LOCATION/FLOW/01JAN2020/1HOUR/RUN1/"
        result = RasDss.check_pathname_format(pathname)

        assert result.passed
        assert result.severity == ValidationSeverity.INFO
        assert "valid" in result.message.lower()

    def test_missing_leading_slash(self):
        """Test pathname missing leading slash"""
        pathname = "/BASIN/LOCATION/FLOW/01JAN2020/1HOUR/RUN1/"
        result = RasDss.check_pathname_format(pathname)

        assert not result.passed
        assert result.severity == ValidationSeverity.ERROR
        assert "must start with" in result.message

    def test_missing_trailing_slash(self):
        """Test pathname missing trailing slash"""
        pathname = "//BASIN/LOCATION/FLOW/01JAN2020/1HOUR/RUN1"
        result = RasDss.check_pathname_format(pathname)

        assert not result.passed
        assert result.severity == ValidationSeverity.ERROR
        assert "must end with" in result.message

    def test_too_few_parts(self):
        """Test pathname with too few parts"""
        pathname = "//BASIN/LOCATION/FLOW/"
        result = RasDss.check_pathname_format(pathname)

        assert not result.passed
        assert result.severity == ValidationSeverity.ERROR
        assert "6 parts" in result.message

    def test_too_many_parts(self):
        """Test pathname with too many parts"""
        pathname = "//BASIN/LOCATION/FLOW/01JAN2020/1HOUR/RUN1/EXTRA/"
        result = RasDss.check_pathname_format(pathname)

        assert not result.passed
        assert result.severity == ValidationSeverity.ERROR

    def test_empty_parts_warning(self):
        """Test pathname with empty parts (warning, not error)"""
        pathname = "//BASIN//FLOW/01JAN2020/1HOUR/RUN1/"
        result = RasDss.check_pathname_format(pathname)

        assert result.passed  # Warning still passes
        assert result.severity == ValidationSeverity.WARNING
        assert "empty" in result.message.lower()

    def test_is_valid_pathname_true(self):
        """Test is_valid_pathname() with valid pathname"""
        pathname = "//BASIN/LOCATION/FLOW/01JAN2020/1HOUR/RUN1/"
        assert RasDss.is_valid_pathname(pathname) is True

    def test_is_valid_pathname_false(self):
        """Test is_valid_pathname() with invalid pathname"""
        pathname = "INVALID/PATH/FORMAT"
        assert RasDss.is_valid_pathname(pathname) is False


class TestFileExistence:
    """Test DSS file existence validation"""

    def test_nonexistent_file(self):
        """Test validation with nonexistent file"""
        dss_file = Path("/nonexistent/path/data.dss")
        result = RasDss.check_file_exists(dss_file)

        assert not result.passed
        assert result.severity == ValidationSeverity.CRITICAL
        assert "not found" in result.message

    def test_directory_not_file(self, tmp_path):
        """Test validation with directory instead of file"""
        result = RasDss.check_file_exists(tmp_path)

        assert not result.passed
        assert result.severity == ValidationSeverity.CRITICAL
        assert "not a file" in result.message

    def test_existing_file(self, tmp_path):
        """Test validation with existing file"""
        # Create a dummy DSS file
        dss_file = tmp_path / "test.dss"
        dss_file.write_text("dummy content")

        result = RasDss.check_file_exists(dss_file)

        assert result.passed
        assert result.severity == ValidationSeverity.INFO
        assert "readable" in result.message
        assert "file_size_mb" in result.details


class TestPathnameExistence:
    """Test DSS pathname existence in catalog"""

    @pytest.fixture(scope="class")
    def bald_eagle_project(self):
        """Extract BaldEagleCrkMulti2D example project"""
        try:
            from ras_commander import RasExamples, init_ras_project
        except ImportError:
            pytest.skip("ras-commander not available")

        # Extract project
        project_path = RasExamples.extract_project("BaldEagleCrkMulti2D")
        ras = init_ras_project(project_path, "6.6")

        return {
            'path': project_path,
            'ras': ras
        }

    def test_existing_pathname(self, bald_eagle_project):
        """Test pathname that exists in DSS file"""
        # Get first DSS boundary from project
        ras_obj = bald_eagle_project['ras']
        dss_boundaries = ras_obj.boundaries_df[ras_obj.boundaries_df['Use DSS'] == True]

        if len(dss_boundaries) == 0:
            pytest.skip("No DSS boundaries in example project")

        boundary = dss_boundaries.iloc[0]
        dss_file = bald_eagle_project['path'] / boundary['DSS File']
        pathname = boundary['DSS Path']

        result = RasDss.check_pathname_exists(dss_file, pathname)

        assert result.passed
        assert result.severity in [ValidationSeverity.INFO, ValidationSeverity.WARNING]

    def test_nonexistent_pathname(self, bald_eagle_project):
        """Test pathname that doesn't exist in DSS file"""
        # Get DSS file from project
        ras_obj = bald_eagle_project['ras']
        dss_boundaries = ras_obj.boundaries_df[ras_obj.boundaries_df['Use DSS'] == True]

        if len(dss_boundaries) == 0:
            pytest.skip("No DSS boundaries in example project")

        boundary = dss_boundaries.iloc[0]
        dss_file = bald_eagle_project['path'] / boundary['DSS File']

        # Use a pathname that definitely doesn't exist
        fake_pathname = "//FAKE/BASIN/FLOW/01JAN1900/1HOUR/NONE/"

        result = RasDss.check_pathname_exists(dss_file, fake_pathname)

        assert not result.passed
        assert result.severity == ValidationSeverity.ERROR
        assert "not found" in result.message.lower()


class TestDataAvailability:
    """Test DSS time series data availability validation"""

    @pytest.fixture(scope="class")
    def bald_eagle_project(self):
        """Extract BaldEagleCrkMulti2D example project"""
        try:
            from ras_commander import RasExamples, init_ras_project
        except ImportError:
            pytest.skip("ras-commander not available")

        project_path = RasExamples.extract_project("BaldEagleCrkMulti2D")
        ras = init_ras_project(project_path, "6.6")

        return {
            'path': project_path,
            'ras': ras
        }

    def test_data_available(self, bald_eagle_project):
        """Test data availability for valid pathname"""
        # Get first DSS boundary
        ras_obj = bald_eagle_project['ras']
        dss_boundaries = ras_obj.boundaries_df[ras_obj.boundaries_df['Use DSS'] == True]

        if len(dss_boundaries) == 0:
            pytest.skip("No DSS boundaries in example project")

        boundary = dss_boundaries.iloc[0]
        dss_file = bald_eagle_project['path'] / boundary['DSS File']
        pathname = boundary['DSS Path']

        result = RasDss.check_data_availability(dss_file, pathname)

        assert result.passed
        assert result.severity in [ValidationSeverity.INFO, ValidationSeverity.WARNING]
        assert result.details.get('data_points', 0) > 0

    def test_date_range_coverage(self, bald_eagle_project):
        """Test data availability with expected date range"""
        # Get first DSS boundary
        ras_obj = bald_eagle_project['ras']
        dss_boundaries = ras_obj.boundaries_df[ras_obj.boundaries_df['Use DSS'] == True]

        if len(dss_boundaries) == 0:
            pytest.skip("No DSS boundaries in example project")

        boundary = dss_boundaries.iloc[0]
        dss_file = bald_eagle_project['path'] / boundary['DSS File']
        pathname = boundary['DSS Path']

        # Set a very wide date range (data should fall within)
        result = RasDss.check_data_availability(
            dss_file,
            pathname,
            expected_start="01JAN1990",
            expected_end="31DEC2030"
        )

        assert result.passed


class TestCombinedValidation:
    """Test combined check_pathname() and is_pathname_available()"""

    @pytest.fixture(scope="class")
    def bald_eagle_project(self):
        """Extract BaldEagleCrkMulti2D example project"""
        try:
            from ras_commander import RasExamples, init_ras_project
        except ImportError:
            pytest.skip("ras-commander not available")

        project_path = RasExamples.extract_project("BaldEagleCrkMulti2D")
        ras = init_ras_project(project_path, "6.6")

        return {
            'path': project_path,
            'ras': ras
        }

    def test_check_pathname_valid(self, bald_eagle_project):
        """Test full validation of valid DSS path"""
        # Get first DSS boundary
        ras_obj = bald_eagle_project['ras']
        dss_boundaries = ras_obj.boundaries_df[ras_obj.boundaries_df['Use DSS'] == True]

        if len(dss_boundaries) == 0:
            pytest.skip("No DSS boundaries in example project")

        boundary = dss_boundaries.iloc[0]
        dss_file = bald_eagle_project['path'] / boundary['DSS File']
        pathname = boundary['DSS Path']

        # Full validation
        report = RasDss.check_pathname(dss_file, pathname)

        # Report should be valid
        assert report.is_valid
        assert len(report.results) >= 3  # At least format, existence, data checks

        # Print report for inspection
        print("\n" + "="*80)
        print(f"Validation Report: {pathname}")
        print("="*80)
        for result in report.results:
            print(f"  {result}")
        print(f"\nSummary: {report.summary}")
        print("="*80)

    def test_check_pathname_invalid_format(self):
        """Test validation with invalid pathname format"""
        report = RasDss.check_pathname(
            "dummy.dss",
            "INVALID/PATH/FORMAT"  # Missing leading/trailing slashes
        )

        # Report should be invalid
        assert not report.is_valid
        assert any(r.check_name == "path_format" for r in report.results)

    def test_check_pathname_nonexistent_file(self):
        """Test validation with nonexistent DSS file"""
        report = RasDss.check_pathname(
            "/nonexistent/file.dss",
            "//BASIN/LOCATION/FLOW/01JAN2020/1HOUR/RUN1/"
        )

        # Report should be invalid
        assert not report.is_valid
        # Should have both format check (passed) and file existence check (failed)
        assert len(report.results) >= 2
        assert report.results[1].check_name == "file_existence"
        assert report.results[1].severity == ValidationSeverity.CRITICAL

    def test_is_pathname_available_true(self, bald_eagle_project):
        """Test is_pathname_available() with valid pathname"""
        # Get first DSS boundary
        ras_obj = bald_eagle_project['ras']
        dss_boundaries = ras_obj.boundaries_df[ras_obj.boundaries_df['Use DSS'] == True]

        if len(dss_boundaries) == 0:
            pytest.skip("No DSS boundaries in example project")

        boundary = dss_boundaries.iloc[0]
        dss_file = bald_eagle_project['path'] / boundary['DSS File']
        pathname = boundary['DSS Path']

        # Boolean check
        assert RasDss.is_pathname_available(dss_file, pathname) is True

    def test_is_pathname_available_false(self, bald_eagle_project):
        """Test is_pathname_available() with invalid pathname"""
        # Get DSS file from project
        ras_obj = bald_eagle_project['ras']
        dss_boundaries = ras_obj.boundaries_df[ras_obj.boundaries_df['Use DSS'] == True]

        if len(dss_boundaries) == 0:
            pytest.skip("No DSS boundaries in example project")

        boundary = dss_boundaries.iloc[0]
        dss_file = bald_eagle_project['path'] / boundary['DSS File']

        # Use fake pathname
        fake_pathname = "//FAKE/BASIN/FLOW/01JAN1900/1HOUR/NONE/"

        # Boolean check
        assert RasDss.is_pathname_available(dss_file, fake_pathname) is False

    def test_validation_report_structure(self, bald_eagle_project):
        """Test validation report structure and properties"""
        # Get first DSS boundary
        ras_obj = bald_eagle_project['ras']
        dss_boundaries = ras_obj.boundaries_df[ras_obj.boundaries_df['Use DSS'] == True]

        if len(dss_boundaries) == 0:
            pytest.skip("No DSS boundaries in example project")

        boundary = dss_boundaries.iloc[0]
        dss_file = bald_eagle_project['path'] / boundary['DSS File']
        pathname = boundary['DSS Path']

        report = RasDss.check_pathname(dss_file, pathname)

        # Test report structure
        assert isinstance(report, ValidationReport)
        assert report.target == pathname
        assert isinstance(report.timestamp, datetime)
        assert len(report.results) > 0

        # Test report properties
        assert isinstance(report.is_valid, bool)
        assert isinstance(report.has_warnings, bool)
        assert isinstance(report.summary, str)

        # Test result filtering
        info_results = report.get_results_by_severity(ValidationSeverity.INFO)
        assert all(r.severity == ValidationSeverity.INFO for r in info_results)


class TestGracefulDegradation:
    """Test graceful degradation when dependencies missing"""

    def test_check_pathname_without_pyjnius(self, monkeypatch):
        """Test pathname checks work even if catalog reading fails"""
        # This test verifies that check_pathname doesn't crash
        # even when pyjnius is unavailable (catalog checks will skip)

        # Test with invalid file (should fail before needing pyjnius)
        report = RasDss.check_pathname(
            "/nonexistent/file.dss",
            "//BASIN/FLOW/01JAN2020/1HOUR/RUN1/"
        )

        # Should still return a report (with file existence error)
        assert isinstance(report, ValidationReport)
        assert not report.is_valid


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
