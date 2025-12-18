from typing import Iterable

from silx.gui import qt


class _PathBrowserBase(qt.QWidget):

    sigPathChanged = qt.Signal()

    def __init__(self):
        super().__init__()

        # Layout
        layout = qt.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Line edit
        self.__lineEdit = qt.QLineEdit()
        layout.addWidget(self.__lineEdit)

        # Browse button
        browseButton = qt.QPushButton("Browse")
        browseButton.setToolTip("Browse file")
        layout.addWidget(browseButton)

        # File system model for completion
        self._model = qt.QFileSystemModel(self)
        self._model.setRootPath("")

        # Completer
        self.__completer = qt.QCompleter(self._model, self.__lineEdit)
        self.__completer.setCompletionMode(qt.QCompleter.CompletionMode.PopupCompletion)
        self.__lineEdit.setCompleter(self.__completer)

        # COnnect Signal / Slots

        browseButton.clicked.connect(self._browse)
        self.__lineEdit.editingFinished.connect(self.sigPathChanged)

    def setPlaceholderText(self, placeHolder: str):
        self.__lineEdit.setPlaceholderText(placeHolder)

    def getPath(self) -> str:
        return self.__lineEdit.text()

    def setPath(self, text: str):
        self.__lineEdit.setText(text)

    def _browse(self):
        raise NotImplementedError("`_browse` need to be override.")


class FileBrowser(_PathBrowserBase):

    def __init__(self):
        super().__init__()
        self._model.setFilter(
            qt.QDir.Filter.NoDotAndDotDot
            | qt.QDir.Filter.AllDirs
            | qt.QDir.Filter.Files
        )
        self.__filter = ""

    def setFilter(self, filterBase: str, filterSuffixes: Iterable[str]):
        """
        To build filter like "Images (*.png *.xpm *.jpg)" for line edit and dialog.

        :param filterBase: filter base like "Images"

        :param filterSuffixes: suffixes like ["*.png", "*.xpm", "*.jpg"]
        """
        self.__filter = f"{filterBase} ({" ".join(filterSuffixes)})"

        self._model.setNameFilters(filterSuffixes)
        self.setPlaceholderText(self.__filter)

    def _browse(self):
        filename, _ = qt.QFileDialog.getOpenFileName(
            self, "Select File", filter=self.__filter
        )
        if filename:
            self.setPath(filename)
            self.sigPathChanged.emit()


class DirectoryBrowser(_PathBrowserBase):

    def __init__(self):
        super().__init__()
        self._model.setFilter(qt.QDir.Filter.NoDotAndDotDot | qt.QDir.Filter.AllDirs)

    def _browse(self):
        dir = qt.QFileDialog.getExistingDirectory(self, "Select Directory")
        if dir:
            self.setPath(dir)
            self.sigPathChanged.emit()
