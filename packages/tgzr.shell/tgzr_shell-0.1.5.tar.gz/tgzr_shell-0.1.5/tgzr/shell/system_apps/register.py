"""

Registers some generic tgzr.shell.app_plugin based on the current system:

"""

from types import ModuleType
import sys
import os
import warnings

from tgzr.shell.app_sdk.exe_app import ShellExeApp, DefaultShellAppInfo
from tgzr.shell.session import Session

# from tgzr.shell.session import Session

from . import run_open


class OpenApp(ShellExeApp):
    def __init__(
        self,
        exe_path: str,
        color: str = "blue-grey-5",
        app_groups: set[str] = set(),
    ):
        app_groups.add("system")
        super().__init__(
            exe_path,
            app_name="open",
            run_module=run_open,
            app_groups=app_groups,
            default_app_info=DefaultShellAppInfo(
                icon="fa-regular fa-folder-open",
                color=color,
            ),
        )

    def cmd(self, session: Session, version: str | None) -> list[str]:
        # TODO: implement something like session.get_context_path(context)
        # and use it here.
        return super().cmd(session, version) + [str(session.home)]


apps = []
platform = sys.platform
if platform == "linux":
    open_app = OpenApp("xdg-open", color="blue-10")
elif platform == "win32":
    open_app = OpenApp("explorer.exe", color="yellow-10")
elif platform == "darwin":
    open_app = OpenApp("open", color="teal-10")
else:
    warnings.warn(
        f"Cannot register system apps: platform {platform!r} not supported yet."
    )


def register_apps():
    return [open_app]
