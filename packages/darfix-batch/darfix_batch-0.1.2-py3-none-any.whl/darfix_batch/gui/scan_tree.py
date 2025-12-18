import logging

import h5py
from silx.gui import qt

from darfix_batch.core.darfix_metadata import DarfixMetadata

_logger = logging.Logger(__name__)


class DarfixScanItem(qt.QStandardItem):

    def __init__(
        self, scan_path: str, detectorPath: str, positionerPath: str, filePath: str
    ):
        super().__init__(scan_path)
        self.metadata = DarfixMetadata(filePath, detectorPath, positionerPath)
        self.setEditable(False)
        self.setSelectable(True)
        self.setToolTip(f"Detector : {detectorPath}\nPositioners : {positionerPath}")
        self.setIcon(
            qt.QApplication.style().standardIcon(
                qt.QStyle.StandardPixmap.SP_FileDialogDetailedView
            )
        )


def _createScanItem(scanPath: str, group: h5py.Group) -> DarfixScanItem | None:
    if not isinstance(group, h5py.Group):
        return None
    positioner = group.get("instrument/positioners")
    if not isinstance(positioner, h5py.Group):
        return None
    positioner_path = positioner.name
    measurement = group.get("measurement")
    if not isinstance(measurement, h5py.Group):
        return None
    for detector_dataset in measurement.values():
        if isinstance(detector_dataset, h5py.Dataset) and detector_dataset.ndim == 3:

            return DarfixScanItem(
                scanPath, detector_dataset.name, positioner_path, group.file.filename
            )

    return None


def _createWarningItem(name: str) -> qt.QStandardItem:
    item = qt.QStandardItem(f"{name} (Cannot be processed by darfix)")
    item.setToolTip(
        f"Cannot find {name}/instrument/positioners or {name}/measurement/{{detector}}"
    )
    item.setEditable(False)
    item.setSelectable(False)
    item.setEnabled(False)
    item.setIcon(
        qt.QApplication.style().standardIcon(qt.QStyle.SP_MessageBoxInformation)
    )

    return item


class ScanTree(qt.QWidget):
    sigSelectionChanged = qt.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.__fileSet = set()

        self.setLayout(qt.QVBoxLayout())

        self.layout().setContentsMargins(0, 0, 0, 0)

        self.__tree = qt.QTreeView()
        self.layout().addWidget(self.__tree)

        self.__model = qt.QStandardItemModel()
        self.__model.setHorizontalHeaderLabels(["Files and Scans"])
        self.__tree.setModel(self.__model)

        self.__tree.setSelectionMode(qt.QAbstractItemView.MultiSelection)
        self.__tree.setTextElideMode(qt.Qt.TextElideMode.ElideLeft)

        # Connect Signals / Slots

        self.__tree.selectionModel().selectionChanged.connect(self.sigSelectionChanged)

    def _createScanItems(self, path, parentItem: qt.QStandardItem):
        if not h5py.is_hdf5(path):
            return
        try:
            with h5py.File(path, "r") as f:
                for scan_path, group in f.items():
                    item = _createScanItem(scan_path, group)
                    if item is None:
                        item = _createWarningItem(scan_path)

                    parentItem.appendRow(item)
                    self.__tree.selectionModel().select(
                        self.__model.indexFromItem(item), qt.QItemSelectionModel.Select
                    )

        except OSError:
            _logger.error(f"Error reading file {path}", exc_info=True)

    def updateFiles(self, paths: tuple[str, ...]):

        rowToRemove = []
        for r in range(self.__model.rowCount()):
            item = self.__model.item(r)
            path = item.text()
            if path not in paths:
                rowToRemove.append(r)
                self.__fileSet.remove(path)

        for row in rowToRemove[::-1]:
            self.__model.removeRow(row)

        for filePath in paths:
            if filePath not in self.__fileSet:
                self.__fileSet.add(filePath)
                fileItem = qt.QStandardItem(filePath)
                fileItem.setCheckable(False)
                fileItem.setEditable(False)
                self._createScanItems(filePath, fileItem)
                self.__model.appendRow(fileItem)
                fileIndex = self.__model.indexFromItem(fileItem)
                self.__tree.expand(fileIndex)

    def getSelectedScans(self) -> list[DarfixMetadata]:
        result = []
        for modelIndex in self.__tree.selectionModel().selectedIndexes():
            item = self.__model.itemFromIndex(modelIndex)
            if not isinstance(item, DarfixScanItem):
                raise RuntimeError(
                    f"Bad item type {type(item)}. Should be DarfixScanItem."
                )

            result.append(item.metadata)
        return result

    def getSelectedCount(self) -> int:
        return len(self.__tree.selectionModel().selectedIndexes())
