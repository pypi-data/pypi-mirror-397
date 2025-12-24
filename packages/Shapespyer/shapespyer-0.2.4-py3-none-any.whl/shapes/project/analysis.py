import sys

from scripts.bash_cli import call_script
from shapes.project.core import BaseAsset
from shapes.project.files import ProjectFileManager
from shapes.project.sample_model import SampleModel


class AnalysisConfiguration(BaseAsset):
    pass


class ForceField(BaseAsset):
    pass


class Analysis(BaseAsset):
    def __init__(self, sample: SampleModel | None = None, **kwargs):
        super().__init__(**kwargs)
        self.force_field = ForceField.load("CHARMM36")
        self.force_field.change_manager(self._manager)

        # TODO update to default when it's available from assets
        # self.configuration = AnalysisConfiguration.load("default")
        self.configuration = AnalysisConfiguration()
        self.configuration.change_manager(self._manager)

        self.steps = 6

        self._sample = sample

    def equilibrate(self, sample_model_name: str | None = None):
        if sample_model_name is not None:
            sample_name = sample_model_name
        elif self._sample is not None:
            sample_name = self._sample.name
        else:
            raise ValueError("A valid Sample Model (name) was not provided")
        cwd = None
        if sys.platform.startswith("win"):
            raise RuntimeError("The script is not available on Windows")
        if isinstance(self._manager, ProjectFileManager):
            cwd = self._manager.stage_equilibration(sample_name)
        else:
            raise RuntimeError("Can't run analysis without a project")

        args = (sample_name, str(0), str(self.steps), str(8), "eq")

        call_script("gmx-equilibrate.bsh", *args, cwd=cwd)
