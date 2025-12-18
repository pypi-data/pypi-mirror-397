import os
from pathlib import Path

from silx.gui import qt

from .file_browser import DirectoryBrowser


class WorkspaceBrowser(qt.QWidget):

    sigSelectionChanged = qt.Signal(tuple)

    def __init__(self, parent=None):
        super().__init__(parent)

        # --- Layout ---
        layout = qt.QVBoxLayout(self)

        layout.setContentsMargins(0, 0, 0, 0)

        # Top: Pick root directory
        selectorLayout = qt.QHBoxLayout()
        self.__rootBrowser = DirectoryBrowser()
        self.__rootBrowser.setPlaceholderText("Workspace directory")

        selectorLayout.addWidget(self.__rootBrowser)

        layout.addLayout(selectorLayout)

        # Tree view
        self.__treeView = qt.QTreeView()
        self.__treeView.setHeaderHidden(False)
        self.__treeView.setSelectionMode(
            qt.QAbstractItemView.SelectionMode.MultiSelection
        )

        layout.addWidget(self.__treeView)

        self.__model = qt.QFileSystemModel()
        self.__model.setNameFilters(["*.h5", ".hdf5"])
        self.__model.setFilter(
            qt.QDir.Filter.Files
            | qt.QDir.Filter.AllDirs
            | qt.QDir.Filter.NoDotAndDotDot
        )

        self.__treeView.setModel(self.__model)

        # Default root directory is current directory.

        self.setRoot(".")

        # Connect Signals / Slots

        self.__treeView.selectionModel().selectionChanged.connect(
            self.__onSelectionChanged
        )
        self.__rootBrowser.sigPathChanged.connect(self.__onRootChanged)

    def __onRootChanged(self):
        """Open a dialog to pick the root directory."""
        self.setRoot(self.__rootBrowser.getPath())

    def setRoot(self, directory):
        """Set the root directory for the lazy file model."""
        self.__treeView.clearSelection()
        self.__model.setRootPath(directory)
        self.__treeView.setRootIndex(self.__model.index(directory))

    def __onSelectionChanged(self):
        """Handle user selecting a file or directory."""

        paths = []

        for selected in self.__treeView.selectedIndexes():
            if selected.column() == 0:
                path = Path(self.__model.filePath(selected))
                if path.is_file():
                    paths.append(str(path))
                else:
                    for filename in os.listdir(path):
                        file_path = path / filename

                        if file_path.is_file() and (
                            file_path.suffix == ".h5" or file_path.suffix == ".hdf5"
                        ):
                            paths.append(str(file_path))
        self.sigSelectionChanged.emit(tuple(paths))

    def _selectOnePath(self, path: str):
        """Utils method for test. Select the given `path`"""
        self.__treeView.selectAll()
        self.__treeView.selectionModel().select(
            self.__model.index(path),
            qt.QItemSelectionModel.SelectionFlag.ClearAndSelect,
        )
