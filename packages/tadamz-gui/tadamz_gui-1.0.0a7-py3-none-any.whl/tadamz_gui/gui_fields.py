import os

from PyQt5.QtCore import QSize
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QStyle,
)


def add_text_field(label, default="", form_layout=None, optional=False, help_text=None):
    """Add a text field to the form."""
    field_label = QLabel(label)
    field = QLineEdit()
    field.setText(default)

    row_layout = QHBoxLayout()
    row_layout.addWidget(field)
    if help_text:
        row_layout.addWidget(_make_help_icon(help_text))

    form_layout.addRow(field_label, row_layout)

    _attach_empty_highlight(field, optional=optional)

    return field


def add_float_field(
    label, default=0.0, form_layout=None, optional=False, help_text=None
):
    """Add a float field with validation to the form."""
    field_label = QLabel(label)
    field = QLineEdit()
    field.setValidator(QDoubleValidator())
    field.setText(str(default))

    row_layout = QHBoxLayout()
    row_layout.addWidget(field)
    if help_text:
        row_layout.addWidget(_make_help_icon(help_text))

    form_layout.addRow(field_label, row_layout)

    _attach_empty_highlight(field, optional=optional)

    return field


def add_combo_field(label, options, default=None, form_layout=None, help_text=None):
    """Add a combo box to the form, with options provided as tuple of display and actual value."""
    field = QComboBox()
    for option in options:
        if isinstance(option, tuple):
            display_value, actual_value = option
            field.addItem(display_value, actual_value)
        else:
            field.addItem(option, option)

    if default:
        index = field.findData(default)
        if index != -1:
            field.setCurrentIndex(index)

    row_layout = QHBoxLayout()
    row_layout.addWidget(field)
    if help_text:
        row_layout.addWidget(_make_help_icon(help_text))

    form_layout.addRow(QLabel(label), row_layout)
    return field


def add_checkbox_field(label, default=False, form_layout=None, help_text=None):
    """Add a checkbox to the form."""
    field_label = QLabel(label)
    field = QCheckBox()
    field.setChecked(default)

    row_layout = QHBoxLayout()
    row_layout.addWidget(field)
    if help_text:
        row_layout.addWidget(_make_help_icon(help_text))

    form_layout.addRow(field_label, row_layout)
    return field


def add_file_field(
    label, file_types=None, form_layout=None, optional=False, help_text=None
):
    """Add a file selection field to the form."""
    field = QLineEdit()
    button = QPushButton("Browse")
    button.clicked.connect(lambda: _browse_file(field, file_types))
    row_layout = QHBoxLayout()
    row_layout.addWidget(field)
    row_layout.addWidget(button)
    if help_text:
        row_layout.addWidget(_make_help_icon(help_text))
    form_layout.addRow(QLabel(label), row_layout)

    _attach_path_highlight(field, optional=optional)

    return field


def add_directory_field(label, form_layout=None, optional=False, help_text=None):
    """Add a directory selection field to the form."""
    field_label = QLabel(label)
    field = QLineEdit()
    button = QPushButton("Browse")
    button.clicked.connect(lambda: _browse_directory(field))
    row_layout = QHBoxLayout()
    row_layout.addWidget(field)
    row_layout.addWidget(button)
    if help_text:
        row_layout.addWidget(_make_help_icon(help_text))
    form_layout.addRow(field_label, row_layout)

    _attach_path_highlight(field, optional=optional)

    return field


def _browse_file(field, file_types=None):
    """Open a file dialog and set the selected file path."""
    file_path, _ = QFileDialog.getOpenFileName(None, "Select File", filter=file_types)
    if file_path:
        field.setText(file_path)


def _browse_directory(field):
    """Open a directory dialog and set the selected directory path."""
    directory_path = QFileDialog.getExistingDirectory(None, "Select Directory")
    if directory_path:
        field.setText(directory_path)


def _attach_empty_highlight(field, optional=False):
    """Highlight orange if empty (when not optional). Also set _is_valid attribute."""

    def highlight():
        if not field.text().strip() and not optional:
            field.setStyleSheet("background-color: orange;")
            field.is_valid = False
        else:
            field.setStyleSheet("")
            field.is_valid = True

    field.textChanged.connect(highlight)
    highlight()


def _attach_path_highlight(field, optional=False):
    """Highlight orange if empty (when not optional), red if path does not exist (if not empty). Also set _is_valid attribute."""

    def highlight():
        text = field.text().strip()
        if not text and not optional:
            field.setStyleSheet("background-color: orange;")
            field.is_valid = False
        elif text and not os.path.exists(text):
            field.setStyleSheet("background-color: red;")
            field.is_valid = False
        else:
            field.setStyleSheet("")
            field.is_valid = True

    field.textChanged.connect(highlight)
    highlight()


def _make_help_icon(help_text):
    label = QLabel()
    icon = QApplication.style().standardIcon(QStyle.SP_MessageBoxInformation)
    pixmap = icon.pixmap(QSize(18, 18))
    label.setPixmap(pixmap)

    help_text_escaped = (
        help_text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("\n", "<br/>")
    )
    html = f'<div style="font-size: 14pt">{help_text_escaped}</div>'
    label.setToolTip(html)

    return label
