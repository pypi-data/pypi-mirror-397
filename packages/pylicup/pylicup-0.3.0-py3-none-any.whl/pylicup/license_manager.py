import logging
from fnmatch import fnmatch
from pathlib import Path

# By default we only add the licenses to the /src *.py files.
__excluded_files = ["__init__.py"]
__pattern = "*.py"


def _get_files_to_change(directories_argv: list[str]) -> list[Path]:
    _files = []
    for directory in directories_argv:
        for found_path in Path(directory).rglob("*"):
            if found_path.name not in __excluded_files and fnmatch(
                found_path.name, __pattern
            ):
                _files.append(found_path)
    return _files

def _wrap_text_as_comment(text_to_wrap: str) -> str:
    return "\"\"\"\n" + text_to_wrap + "\n\"\"\"\n"

def _get_licenses_content(header_licenses_argv: list[str]) -> list[str]:
    return [_wrap_text_as_comment(Path(hl_argv).read_text()) for hl_argv in header_licenses_argv]

def _get_file_content_without_licenses(
    file_to_change: Path, license_headers: list[str]
) -> str:
    _file_content = file_to_change.read_text()
    if len(license_headers) > 1:
        # We need to replace licenses if found.
        for header_to_replace in license_headers[1:]:
            _file_content = _file_content.replace(header_to_replace, "")
    return _file_content


def license_header_manager(header_licenses: list[str], directory_files: list[str]):
    """Insert the license header provided in the argument to all the files
    in the directory (also provided in the arguments).

    Arguments:
        argv {[str]} -- default input from command line
    """
    _files_to_change = _get_files_to_change(directory_files)
    logging.info(f"Found {len(_files_to_change)} files to change.")
    _licenses_content = _get_licenses_content(header_licenses)

    files_changed = []
    for file_to_change in _files_to_change:
        unlicensed_file_content = _get_file_content_without_licenses(
            file_to_change, _licenses_content
        )
        if not _licenses_content[0] in unlicensed_file_content:
            # Add license if not present.
            licensed_file_content = (
                _licenses_content[0] +
                "\n" +
                unlicensed_file_content
            )
            file_to_change.write_text(licensed_file_content)
            logging.info(f"Changed license header for: {file_to_change}")
            files_changed.append(file_to_change)
    logging.info(f"Changed #{len(files_changed)} files.")
