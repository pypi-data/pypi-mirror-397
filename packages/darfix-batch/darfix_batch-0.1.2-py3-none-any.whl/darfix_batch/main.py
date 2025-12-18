import sys

from silx import config
from silx.gui import qt

from .gui.main_window import MainWindow


def main(argv=None):

    config._MPL_TIGHT_LAYOUT = True

    app = qt.QApplication([])
    app.setOrganizationName("ESRF")
    app.setOrganizationDomain("esrf.fr")
    app.setApplicationName("darfix_batch")

    mainWindow = MainWindow()

    mainWindow.show()

    result = app.exec()

    return result


if __name__ == "__main__":
    sys.exit(main())
