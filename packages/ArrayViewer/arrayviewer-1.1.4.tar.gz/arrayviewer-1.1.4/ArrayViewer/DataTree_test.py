import sys
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget, QPushButton, QTreeWidgetItemIterator
from PyQt5.QtCore import Qt
from collections import defaultdict


class ShapeAwareTreeWidget(QTreeWidget):
    def __init__(self, data_dict, parent=None):
        super().__init__(parent)
        self.data_dict = data_dict
        self.setHeaderLabels(["Key", "Shape/Value"])
        self.setColumnCount(2)

        # Analyze shapes and build tree
        self.shape_groups = self._analyze_shapes(data_dict)
        self._populate_tree(data_dict)

        self.itemChanged.connect(self._handle_item_changed)
        self.expandAll()

    def _get_shape(self, value):
        """Get shape of a value, handling various types."""
        if isinstance(value, np.ndarray):
            return value.shape
        elif isinstance(value, dict):
            return "dict"
        else:
            return "scalar"

    def _analyze_shapes(self, data, prefix=""):
        """Recursively analyze the structure and group items by shape."""
        shape_groups = defaultdict(list)

        def recurse(obj, path):
            if isinstance(obj, dict):
                # Check if all children have the same shape
                child_shapes = {}
                for key, value in obj.items():
                    child_path = f"{path}.{key}" if path else key
                    shape = self._get_shape(value)
                    child_shapes[child_path] = shape
                    recurse(value, child_path)

                # If all children are arrays with the same shape, this dict is checkable
                array_shapes = [s for s in child_shapes.values() if isinstance(s, tuple)]
                if array_shapes and len(set(array_shapes)) == 1:
                    shape_groups[array_shapes[0]].append(path)
            elif isinstance(obj, np.ndarray):
                shape_groups[obj.shape].append(path)

        recurse(data, prefix)
        return shape_groups

    def _populate_tree(self, data, parent=None, path=""):
        """Recursively populate the tree with data."""
        for key, value in data.items():
            current_path = f"{path}.{key}" if path else key

            if parent is None:
                item = QTreeWidgetItem(self)
            else:
                item = QTreeWidgetItem(parent)

            item.setText(0, str(key))
            item.setData(0, Qt.UserRole, current_path)

            if isinstance(value, dict):
                item.setText(1, f"[{len(value)} items]")
                self._populate_tree(value, item, current_path)

                # Check if this dict's children all have the same shape
                if self._has_uniform_child_shapes(value):
                    item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                    item.setCheckState(0, Qt.Unchecked)
            elif isinstance(value, np.ndarray):
                item.setText(1, str(value.shape))
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                item.setCheckState(0, Qt.Unchecked)
            else:
                item.setText(1, f"{type(value).__name__}: {value}")
                # Scalars can be checked too
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                item.setCheckState(0, Qt.Unchecked)

    def _has_uniform_child_shapes(self, obj):
        """Check if all direct children (or nested children) have the same shape."""
        if not isinstance(obj, dict):
            return False

        shapes = []
        for value in obj.values():
            if isinstance(value, np.ndarray):
                shapes.append(value.shape)
            elif isinstance(value, (int, float, str)):
                shapes.append("scalar")

        # All children must be arrays with the same shape
        return len(shapes) > 0 and len(set(shapes)) == 1 and isinstance(shapes[0], tuple)

    def _handle_item_changed(self, item, column):
        """Handle checkbox state changes and update related items."""
        if column != 0:
            return

        # Block signals to prevent recursion
        self.blockSignals(True)

        current_path = item.data(0, Qt.UserRole)
        current_value = self._get_value_from_path(current_path)
        current_shape = self._get_shape(current_value)

        check_state = item.checkState(0)

        # If checking an item, uncheck all items with different shapes
        if check_state == Qt.Checked:
            self._update_checkable_items(current_shape, item)

        self.blockSignals(False)

    def _update_checkable_items(self, selected_shape, selected_item):
        """Enable/disable items based on shape compatibility."""
        iterator = QTreeWidgetItemIterator(self)

        while iterator.value():
            item = iterator.value()
            if item != selected_item and item.flags() & Qt.ItemIsUserCheckable:
                item_path = item.data(0, Qt.UserRole)
                item_value = self._get_value_from_path(item_path)
                item_shape = self._get_shape(item_value)

                # Disable items with different shapes
                if item_shape != selected_shape:
                    item.setFlags(item.flags() & ~Qt.ItemIsUserCheckable)
                    item.setCheckState(0, Qt.Unchecked)

            iterator += 1

    def _get_value_from_path(self, path):
        """Retrieve value from data_dict using dot-separated path."""
        keys = path.split('.')
        value = self.data_dict
        for key in keys:
            value = value[key]
        return value

    def get_checked_items(self):
        """Return list of paths for all checked items."""
        checked = []
        iterator = QTreeWidgetItemIterator(self, QTreeWidgetItemIterator.Checked)

        while iterator.value():
            item = iterator.value()
            checked.append(item.data(0, Qt.UserRole))
            iterator += 1

        return checked


# Example usage
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Shape-Aware Tree Selection")
        self.setGeometry(100, 100, 600, 400)

        # Sample data
        data = {
            "A": {
                "B": np.random.rand(5, 3),
                "C": np.random.rand(5, 3),
                "D": np.random.rand(5, 3)
            },
            "E": np.random.rand(5, 3, 3),
            "F": np.random.rand(2, 1, 5),
            "G": {
                "H": np.random.rand(5, 3, 3),
                "I": np.random.rand(5, 3, 3)
            },
            "J": 42,
            "K": "test"
        }

        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)

        self.tree = ShapeAwareTreeWidget(data)
        layout.addWidget(self.tree)

        btn = QPushButton("Get Checked Items")
        btn.clicked.connect(self.show_checked)
        layout.addWidget(btn)

        self.setCentralWidget(central_widget)

    def show_checked(self):
        checked = self.tree.get_checked_items()
        print("Checked items:", checked)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
