from pathlib import Path

from shapes.project.analysis import Analysis
from shapes.project.files import ProjectFileManager
from shapes.project.sample_model import SampleModel, Structure


class Project:
    def __init__(self, path: str | Path | None = None):
        self.title = None
        self.description = None

        self._manager = ProjectFileManager(path)

        self.sample_model = SampleModel(
            Structure("ring", manager=self._manager),
            manager=self._manager,
        )
        self.analysis = Analysis(sample=self.sample_model, manager=self._manager)

    def save(self):
        raise NotImplementedError("Can't be implemented without serialization")

    def save_as(self, path: str | Path):
        self._manager.move_all(path)
        raise NotImplementedError("Can't be implemented without serialization")

    @property
    def summary(self):
        return Summary(self)

    @property
    def path(self):
        return self._manager._items_root


class Summary:
    def __init__(self, project):
        raise NotImplementedError

    def show_report(self):
        raise NotImplementedError
