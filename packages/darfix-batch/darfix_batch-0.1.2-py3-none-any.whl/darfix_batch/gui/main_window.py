import re
from pathlib import Path

from ewoks import load_graph
from silx.gui import qt

from darfix_batch.common.gui.workflow_executor import WorkflowExecutor
from darfix_batch.gui.darfix_jobs_list_widget import DarfixJobListWidget
from darfix_batch.gui.output_group import OutputGroup
from darfix_batch.gui.scan_tree import ScanTree
from darfix_batch.gui.workspace_browser import WorkspaceBrowser

from ..core.darfix_metadata import convert_metadata_to_graph_inputs


class MainWindow(qt.QMainWindow):

    def __init__(self):
        super().__init__()

        self._workspace = WorkspaceBrowser()
        self._scanTree = ScanTree()
        self._outputGroup = OutputGroup()
        self._tipsLabel = qt.QLabel("Select scans to process.")
        self._tipsLabel.setStyleSheet("QLabel {color: grey}")
        self._executor = WorkflowExecutor()
        self._jobListWidget = DarfixJobListWidget(self._executor)

        centralWidget = qt.QWidget()
        mainLayout = qt.QGridLayout()
        centralWidget.setLayout(mainLayout)
        self.setCentralWidget(centralWidget)

        mainLayout.addWidget(self._workspace, 0, 0)
        mainLayout.addWidget(self._scanTree, 0, 1)
        mainLayout.addWidget(self._tipsLabel, 1, 0, 1, 2)
        mainLayout.addWidget(self._outputGroup, 2, 0, 1, 2)

        rightToolBar = qt.QToolBar()
        self.setContextMenuPolicy(qt.Qt.NoContextMenu)
        self.addToolBar(qt.Qt.ToolBarArea.RightToolBarArea, rightToolBar)

        rightToolBar.addWidget(self._jobListWidget)

        self._workspace.setRoot("/home/ruyer/tmp")

        # Connect Signals / Slots

        self._workspace.sigSelectionChanged.connect(self.__onFileSelectionChanged)
        self._scanTree.sigSelectionChanged.connect(self.__onScanSelectionChanged)
        self._outputGroup.sigRun.connect(self.executeDarfixWorkflows)

    def executeDarfixWorkflows(self):
        for scanMetadata in self._scanTree.getSelectedScans():
            graph = load_graph(self._outputGroup.worflowPath())
            fileBaseName = Path(scanMetadata.raw_input_file).stem
            fileBaseName = re.sub(r"[^a-zA-Z0-9_-]", "", fileBaseName)  # Clean filename
            outputDir = str(
                Path(self._outputGroup.outputDirectory())
                / fileBaseName
                / scanMetadata.get_scan_name()
            )
            inputs = convert_metadata_to_graph_inputs(scanMetadata, outputDir)
            self._executor.submit(True, graph=graph, inputs=inputs, output_tasks=True)

    def __onFileSelectionChanged(self, paths: tuple[str, ...]):
        self._scanTree.updateFiles(paths)

    def __onScanSelectionChanged(self):
        self._tipsLabel.setText(f"{self._scanTree.getSelectedCount()} scans selected.")
