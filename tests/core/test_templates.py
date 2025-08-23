from google_dork_automation.core.templates import load_templates

def test_load_templates_success():
    """
    Tests that the dork templates are loaded correctly from the YAML file.
    """
    templates = load_templates()

    assert isinstance(templates, dict)
    assert len(templates) > 0, "Templates should not be empty"

    # Check for the presence of the main keys
    expected_keys = ["log_files", "sqli_errors", "exposed_panels"]
    for key in expected_keys:
        assert key in templates

    # Check the structure of one of the templates
    log_files_template = templates["log_files"]
    assert "description" in log_files_template
    assert "dorks" in log_files_template
    assert isinstance(log_files_template["dorks"], list)
    assert len(log_files_template["dorks"]) > 0
    assert 'allintext:password filetype:log' in log_files_template["dorks"]

def test_load_templates_returns_dict_on_error(mocker):
    """
    Tests that load_templates returns an empty dict if an error occurs.
    """
    # Mock importlib.resources to simulate a FileNotFoundError
    mocker.patch("importlib.resources.files", side_effect=FileNotFoundError("File not found"))

    templates = load_templates()

    assert isinstance(templates, dict)
    assert len(templates) == 0
