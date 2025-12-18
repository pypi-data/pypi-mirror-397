import os
import tempfile
from pathlib import Path

import pytest  # noqa F811

from darfix_batch.gui.main_window import MainWindow

from . import resources
from .utils import create_dataset


def test_run_workflows(qtbot):
    window = MainWindow()
    qtbot.addWidget(window)
    with tempfile.TemporaryDirectory() as tmpdirname:
        tmp_dataset_path = str(Path(tmpdirname) / "dset.h5")
        create_dataset(tmp_dataset_path)
        window._workspace.setRoot(tmpdirname)

        with qtbot.waitSignal(window._workspace.sigSelectionChanged, timeout=1000):
            with qtbot.waitSignal(window._scanTree.sigSelectionChanged, timeout=1000):
                window._workspace._selectOnePath(tmp_dataset_path)

        assert window._scanTree.getSelectedCount() == 2

        window._outputGroup.setWorkflowPath(
            resources.resource_filename("grainplot.ows")
        )
        window._outputGroup.setOutputDirectory(tmpdirname)

        with qtbot.waitSignal(window._executor.finished, timeout=10000):
            with qtbot.waitSignal(window._executor.finished, timeout=10000):
                window._outputGroup.sigRun.emit()

        output_scan_1 = str(Path(tmpdirname) / "dset/1.1/maps.h5")
        assert os.path.exists(output_scan_1)

        output_scan_2 = str(Path(tmpdirname) / "dset/2.1/maps.h5")
        assert os.path.exists(output_scan_2)
