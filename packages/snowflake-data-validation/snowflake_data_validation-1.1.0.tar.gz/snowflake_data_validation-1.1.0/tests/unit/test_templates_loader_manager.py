from pathlib import Path
import tempfile

from deepdiff import DeepDiff
import pandas as pd

from snowflake.snowflake_data_validation.utils.constants import Platform
from snowflake.snowflake_data_validation.utils.model.templates_loader_manager import (
    TemplatesLoaderManager,
)

ASSETS_DIRECTORY_NAME = "assets"
TEST_TEMPLATES_LOADER_MANAGER_DIRECTORY_NAME = "test_templates_loader_manager"
CUSTOM_TEMPLATES_LOADER_MANAGER_DIRECTORY_NAME = "custom_templates_loader"


def test_template_loader_manager_generation():

    templates_directory_path = (
        Path(__file__)
        .parent.joinpath(ASSETS_DIRECTORY_NAME)
        .joinpath(TEST_TEMPLATES_LOADER_MANAGER_DIRECTORY_NAME)
    )

    platform = Platform.SNOWFLAKE

    templates_loader_manager = TemplatesLoaderManager(
        templates_directory_path=templates_directory_path, platform=platform
    )

    assert templates_loader_manager is not None
    assert templates_loader_manager.templates_directory_path == templates_directory_path
    assert templates_loader_manager.platform == platform

    expected_datatypes_normalization_templates = {
        "TYPE1": r"""TO_CHAR("{{ col_name }}")""",
        "TYPE2": r"""TO_CHAR("{{ col_name }}", 'YYYY-MM-DD')""",
        "TYPE3": r"""TO_CHAR("{{ col_name }}", '{{ column_numeric_format }}')""",
        "TYPE4": r"""TO_CHAR("{{ col_name }}")""",
    }

    datatypes_normalization_templates_diff = DeepDiff(
        expected_datatypes_normalization_templates,
        templates_loader_manager.datatypes_normalization_templates,
        ignore_order=True,
    )

    assert datatypes_normalization_templates_diff == {}

    expected_metrics_templates = pd.DataFrame(
        {
            "type": ["TYPE1", "TYPE1", "TYPE2", "TYPE2"],
            "metric": ["METRIC1", "METRIC2", "METRIC1", "METRIC2"],
            "template": [
                'COUNT_IF("{{ col_name }}" = TRUE)',
                'COUNT_IF("{{ col_name }}" = FALSE)',
                'COUNT_IF("{{ col_name }}" = TRUE)',
                'COUNT_IF("{{ col_name }}" = FALSE)',
            ],
            "normalization": [
                "TO_CHAR({{ metric_query }}, 'FM9999999999999999999999999999.0000')",
                "TO_CHAR({{ metric_query }}, 'FM9999999999999999999999999999.0000')",
                "TO_CHAR({{ metric_query }}, '{{ column_numeric_format }}')",
                "TO_CHAR({{ metric_query }}, '{{ column_numeric_format }}')",
            ],
            "column_modifier": [None, None, None, None],
        }
    )

    assert expected_metrics_templates.equals(templates_loader_manager.metrics_templates)


def test_template_loader_manager_with_custom_templates():
    # Set up paths for both regular and custom templates
    templates_directory_path = (
        Path(__file__)
        .parent.joinpath(ASSETS_DIRECTORY_NAME)
        .joinpath(TEST_TEMPLATES_LOADER_MANAGER_DIRECTORY_NAME)
    )

    # Assuming there's a subdirectory for custom templates in the test assets
    custom_templates_directory_path = (
        Path(__file__)
        .parent.joinpath(ASSETS_DIRECTORY_NAME)
        .joinpath(CUSTOM_TEMPLATES_LOADER_MANAGER_DIRECTORY_NAME)
    )

    platform = Platform.SNOWFLAKE

    # Create templates loader manager with custom templates directory
    templates_loader_manager = TemplatesLoaderManager(
        templates_directory_path=templates_directory_path,
        platform=platform,
        custom_templates_directory_path=custom_templates_directory_path,
    )

    # Verify basic properties
    assert templates_loader_manager is not None
    assert templates_loader_manager.templates_directory_path == templates_directory_path
    assert (
        templates_loader_manager.custom_templates_directory_path
        == custom_templates_directory_path
    )
    assert templates_loader_manager.platform == platform

    # If custom templates override the default ones, verify that the custom values are used
    # This would depend on the specific implementation of how custom templates are merged
    # with default ones, but here's an example check:

    # Assuming custom templates contain a TYPE5 datatype normalization
    if "TYPE5" in templates_loader_manager.datatypes_normalization_templates:
        assert (
            templates_loader_manager.datatypes_normalization_templates["TYPE5"]
            == r"""TO_CHAR("{{ col_name }}", 'CUSTOM_FORMAT')"""
        )

    # Verify that default templates are still loaded
    assert "TYPE1" in templates_loader_manager.datatypes_normalization_templates

    # Check if metrics templates include both default and custom metrics
    metrics_df = templates_loader_manager.metrics_templates
    assert not metrics_df.empty

    # Check if a custom metric exists in the metrics templates
    # This assumes the custom templates define a CUSTOM_METRIC for TYPE1
    custom_metric_exists = any(
        (metrics_df["type"] == "TYPE1") & (metrics_df["metric"] == "CUSTOM_METRIC")
    )

    # Validate the presence of the custom metric in the test data
    if not custom_metric_exists:
        raise AssertionError("Custom metric not found in loaded templates")


def test_template_loader_manager_copy_custom_jinja_templates():
    """Test that TemplatesLoaderManager can copy custom Jinja templates to a target directory."""
    templates_directory_path = (
        Path(__file__)
        .parent.joinpath(ASSETS_DIRECTORY_NAME)
        .joinpath(TEST_TEMPLATES_LOADER_MANAGER_DIRECTORY_NAME)
    )

    custom_templates_directory_path = (
        Path(__file__)
        .parent.joinpath(ASSETS_DIRECTORY_NAME)
        .joinpath(CUSTOM_TEMPLATES_LOADER_MANAGER_DIRECTORY_NAME)
    )

    platform = Platform.SNOWFLAKE

    templates_loader_manager = TemplatesLoaderManager(
        templates_directory_path=templates_directory_path,
        platform=platform,
        custom_templates_directory_path=custom_templates_directory_path,
    )

    # Test copying custom Jinja templates to a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        target_dir = Path(temp_dir)

        # Copy custom templates
        templates_loader_manager.copy_custom_jinja_templates_to_directory(target_dir)

        # Verify that the custom template was copied
        copied_template = target_dir / "snowflake_table_metadata_query.sql.j2"
        assert copied_template.exists()

        # Verify the content matches the custom template
        original_content = (
            custom_templates_directory_path / "snowflake_table_metadata_query.sql.j2"
        ).read_text()
        copied_content = copied_template.read_text()
        assert copied_content == original_content
        assert "CUSTOM_TEMPLATE" in copied_content


def test_template_loader_manager_copy_no_custom_templates():
    """Test that TemplatesLoaderManager handles cases with no custom templates gracefully."""
    templates_directory_path = (
        Path(__file__)
        .parent.joinpath(ASSETS_DIRECTORY_NAME)
        .joinpath(TEST_TEMPLATES_LOADER_MANAGER_DIRECTORY_NAME)
    )

    platform = Platform.SNOWFLAKE

    # Create template loader without custom templates directory
    templates_loader_manager = TemplatesLoaderManager(
        templates_directory_path=templates_directory_path,
        platform=platform,
        custom_templates_directory_path=None,
    )

    # Test copying when there are no custom templates
    with tempfile.TemporaryDirectory() as temp_dir:
        target_dir = Path(temp_dir)

        # This should not raise an exception
        templates_loader_manager.copy_custom_jinja_templates_to_directory(target_dir)

        # Directory should exist but be empty (only default files if any)
        assert target_dir.exists()


def test_template_loader_manager_copy_nonexistent_custom_directory():
    """Test that TemplatesLoaderManager handles non-existent custom template directories gracefully."""
    templates_directory_path = (
        Path(__file__)
        .parent.joinpath(ASSETS_DIRECTORY_NAME)
        .joinpath(TEST_TEMPLATES_LOADER_MANAGER_DIRECTORY_NAME)
    )

    # Use a non-existent directory
    custom_templates_directory_path = Path("/non/existent/directory")

    platform = Platform.SNOWFLAKE

    templates_loader_manager = TemplatesLoaderManager(
        templates_directory_path=templates_directory_path,
        platform=platform,
        custom_templates_directory_path=custom_templates_directory_path,
    )

    # Test copying when custom directory doesn't exist
    with tempfile.TemporaryDirectory() as temp_dir:
        target_dir = Path(temp_dir)

        # This should not raise an exception
        templates_loader_manager.copy_custom_jinja_templates_to_directory(target_dir)

        # Directory should exist but be empty
        assert target_dir.exists()
