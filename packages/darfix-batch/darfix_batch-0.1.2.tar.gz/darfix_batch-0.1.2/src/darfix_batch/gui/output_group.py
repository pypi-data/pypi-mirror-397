from silx.gui import qt

from .file_browser import DirectoryBrowser
from .file_browser import FileBrowser


class OutputGroup(qt.QWidget):
    sigRun = qt.Signal()

    def __init__(
        self,
    ):
        super().__init__()
        runButton = qt.QPushButton("RUN")
        self.__workflowBrowser = FileBrowser()
        self.__workflowBrowser.setFilter("Worflow", ["*.ows"])

        self.__outputDirBrowser = DirectoryBrowser()
        self.__outputDirBrowser.setPlaceholderText("Output Directory")

        layout = qt.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        layout.addWidget(self.__workflowBrowser)
        layout.addWidget(self.__outputDirBrowser)
        layout.addWidget(runButton)
        layout.addStretch(1)

        # Connect Signals / Slots

        runButton.clicked.connect(self.sigRun)

    def outputDirectory(self) -> str:
        return self.__outputDirBrowser.getPath()

    def setOutputDirectory(self, path: str):
        self.__outputDirBrowser.setPath(path)

    def worflowPath(self) -> str:
        return self.__workflowBrowser.getPath()

    def setWorkflowPath(self, path: str):
        self.__workflowBrowser.setPath(path)
