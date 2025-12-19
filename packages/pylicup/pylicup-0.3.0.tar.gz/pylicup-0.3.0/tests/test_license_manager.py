import shutil
import pytest
from pylicup.license_manager import _get_licenses_content, _get_file_content_without_licenses, _wrap_text_as_comment
from tests import test_results, test_data

class TestLicenseManager:

    def test_get_files_to_change(self):
        pass

    def test_wrap_text_as_comment(self):
        # 1. Define test data
        _text = "this is\n a text\t sample"
        _expected_result = f"\"\"\"\n{_text}\n\"\"\"\n"

        # 2. Run test
        _result = _wrap_text_as_comment(_text)

        # 3. Verify expectations
        assert _expected_result == _result

    def test_get_licenses_content_returns_wrapped_text(self):
        # 1. Define test data.
        _test_file = test_data / "license_example"
        assert _test_file.exists()
        _test_text = _test_file.read_text()

        # 2. Run test.
        _result = _get_licenses_content([_test_file])

        # 3. Verify expectations.
        assert len(_result) == 1
        assert _test_text in _result[0]
        assert _test_text != _result[0]
        assert _wrap_text_as_comment(_test_text) == _result[0]

    def test_get_file_content_without_licenses_replaces_license_if_present(self, request: pytest.FixtureRequest):
        # 1. Define test data.
        _test_file = test_results / request.node.name / "license_file"
        if _test_file.exists():
            shutil.rmtree(_test_file.parent)
        _test_file.parent.mkdir(parents=True)
        _test_file.touch()
        
        # Add two licenses.
        _my_old_license = _wrap_text_as_comment("Laboris consequat aliqua labore et quis officia exercitation excepteur minim irure.")
        _my_older_license = _wrap_text_as_comment("Irure consectetur amet consectetur velit labore.")
        _my_new_license = "In enim aliquip laborum duis adipisicing nisi."

        _test_file.write_text(_my_old_license + _my_older_license)
        
        # 2. Run test.
        _result = _get_file_content_without_licenses(_test_file, [_my_new_license, _my_old_license, _my_older_license])

        # 3. Verify expectations
        assert _my_old_license not in _result
        assert _my_older_license not in _result

    def test_get_file_content_without_licenses_replaces_only_given_license(self, request: pytest.FixtureRequest):
        # 1. Define test data.
        _test_file = test_results / request.node.name / "license_file"
        if _test_file.exists():
            shutil.rmtree(_test_file.parent)
        _test_file.parent.mkdir(parents=True)
        _test_file.touch()
        
        # Add two licenses.
        _my_old_license = _wrap_text_as_comment("Laboris consequat aliqua labore et quis officia exercitation excepteur minim irure.")
        _my_older_license = _wrap_text_as_comment("Irure consectetur amet consectetur velit labore.")
        _my_new_license = "In enim aliquip laborum duis adipisicing nisi."

        _test_file.write_text(_my_old_license + _my_older_license)
        
        # 2. Run test.
        _result = _get_file_content_without_licenses(_test_file, [_my_new_license, _my_old_license])

        # 3. Verify expectations
        assert _my_old_license not in _result
        assert _my_older_license in _result
