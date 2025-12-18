from ._windows_utils import _find_app_starting_with

def _find_zelesis_installation():
    return _find_app_starting_with("Zelesis Neo")

def _get_zelesis_version():
    path = _find_zelesis_installation() / "version.txt"

    try:
        return path.read_text(encoding="utf-8").strip() # strip it to avoid \n if it occurs
    except FileNotFoundError:
        raise RuntimeError("Zelesis installation found, but version.txt is missing")