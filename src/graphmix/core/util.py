"""Everything here was copied directly from the `click` library, which is
licensed under the BSD 3-Clause "New" or "Revised" License. The original source
code can be found at https://github.com/pallets/click."""

import os
import sys
from enum import Enum
from pathlib import Path

CYGWIN = sys.platform.startswith("cygwin")
WIN = sys.platform.startswith("win")


def _posixify(name: str) -> str:
    return "-".join(name.split()).lower()


def get_app_dir(
    app_name: str, roaming: bool = True, force_posix: bool = False
) -> str:
    r"""Returns the config folder for the application.  The default behavior
    is to return whatever is most appropriate for the operating system.

    To give you an idea, for an app called ``"Foo Bar"``, something like
    the following folders could be returned:

    Mac OS X:
      ``~/Library/Application Support/Foo Bar``
    Mac OS X (POSIX):
      ``~/.foo-bar``
    Unix:
      ``~/.config/foo-bar``
    Unix (POSIX):
      ``~/.foo-bar``
    Windows (roaming):
      ``C:\Users\<user>\AppData\Roaming\Foo Bar``
    Windows (not roaming):
      ``C:\Users\<user>\AppData\Local\Foo Bar``

    . versionadded:: 2.0

    :param app_name: the application name.  This should be properly capitalized
                     and can contain whitespace.
    :param roaming: controls if the folder should be roaming or not on Windows.
                    Has no effect otherwise.
    :param force_posix: if this is set to `True` then on any POSIX system the
                        folder will be stored in the home folder with a leading
                        dot instead of the XDG config home or darwin's
                        application support folder.
    """
    if WIN:
        key = "APPDATA" if roaming else "LOCALAPPDATA"
        folder = os.environ.get(key)
        if folder is None:
            folder = Path("~").expanduser()
        return Path(folder) / app_name
    if force_posix:
        return Path(Path(f"~/.{_posixify(app_name)}").expanduser())
    if sys.platform == "darwin":
        return (
            Path(Path("~/Library/Application Support")).expanduser() / app_name
        )

    return (
        Path(os.environ.get("XDG_CONFIG_HOME", Path("~/.config").expanduser()))
        / _posixify(app_name),
    )


class StrEnum(str, Enum):
    """
    A string-based Enum copied from
    https://www.cosmicpython.com/blog/2020-10-27-i-hate-enums.html
    """

    def __str__(self) -> str:
        return str.__str__(self)
