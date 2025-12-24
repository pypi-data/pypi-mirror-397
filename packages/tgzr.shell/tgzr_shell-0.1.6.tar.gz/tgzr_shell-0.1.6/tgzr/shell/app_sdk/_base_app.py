from __future__ import annotations
from typing import TYPE_CHECKING
from types import ModuleType
import inspect

import click

from tgzr.cli.utils import TGZRCliGroup

from ..session import Session

from .exceptions import MissingRunNativeModule
from .app_info import ShellAppContext, ShellAppInfo, DefaultShellAppInfo

if TYPE_CHECKING:
    from ..session import Session


class _BaseShellApp:

    def __init__(
        self,
        app_name: str,
        run_module: ModuleType | None,
        app_id: str | None = None,
        app_groups: set[str] = set(),
        default_app_info: DefaultShellAppInfo | None = None,
    ):
        """
        Create an App which will be accessible in the tgzr CLI.

        `app_name`:
            The name of the app, used to name the CLI command.

        `app_id`:
            The unic id associated with the app.
            The default value is the name of the module defining the
            app. This should be unic enough.

        `run_module`:
            The python module used to run the app.
            Must be a valid modules with appropriate safeguards.
            NOTE: using None will raise an exception showing you
            how to implement this module.

        `app_groups`:
            A set of groups where this app should be found.
            Groups with double-underscopre (like "_EXE_") are managed by tgzr.

        `app_info`:
            Provides the default info about this app.
            See _BaseShellApp.get_info()
        """
        frame: inspect.FrameInfo = inspect.stack()[1]
        if app_name is None:
            app_name = frame.function
            # print("---> AUTO APP NAME:", repr(app_name))

        if app_id is None:
            # FIXME: the module used here is wrong!
            module = inspect.getmodule(frame[0])
            app_id = (module and module.__name__ or "???") + ":" + app_name
            # print("---> AUTO APP ID:", app_id)

        if run_module is None:
            raise MissingRunNativeModule(self)
        self.run_native_module = run_module

        self.app_name = app_name
        self.app_id = app_id
        self.app_groups = app_groups
        self._default_app_info = default_app_info or DefaultShellAppInfo()

    def installed_versions(self, session: Session) -> set[str]:
        """
        Return the list of installed versions.
        Default is to return an empty set, which means this app
        does not support multiple versions
        """
        return set()

    def cli_run_cmd_installed(
        self, created_cmd: click.Command, root_group: TGZRCliGroup
    ):
        """
        Called when tgzr.shell.cli_plugin.app_cli has created and
        registered a cli command to execute this app.

        Subclasses can override this to alter the cmd or set it as default
        on the root group.

        Default does nothing.
        """
        pass

    def get_info(self, context: ShellAppContext) -> ShellAppInfo:
        """
        Subclasses can reimplement this to provide
        information used by GUIs to display (or hide) this app
        in the given context.

        The default behavior is to return a copy of the `app_info`
        provided in the constructor, and hide the app if
        context.context_name is not part of the app.app_groups set.
        """
        # print("???", self.app_name, self.app_groups, context.context_name)
        app_info = ShellAppInfo(
            app=self,
            title=self._default_app_info.title or self.app_name.title(),
            icon=self._default_app_info.icon,
            color=self._default_app_info.color,
            hidden=context.context_name not in self.app_groups,
            installed_versions=self.installed_versions(context.session),
        )
        return app_info

    def run_app(self, session: Session):
        raise NotImplementedError()
