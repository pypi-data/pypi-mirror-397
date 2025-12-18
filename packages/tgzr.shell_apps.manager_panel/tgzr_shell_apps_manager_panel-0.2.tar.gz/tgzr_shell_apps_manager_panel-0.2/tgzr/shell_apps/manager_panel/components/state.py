from dataclasses import dataclass

from tgzr.shell.session import Session
from tgzr.shell.studio import Studio
from tgzr.shell.project import Project


@dataclass
class State:
    session: Session | None = None
    studio: Studio | None = None
    project: Project | None = None
    package_name: str | None = None
