"""Shared styles for modal choice dialogs."""

DIALOG_STYLE = """
QDialog {
    background: #f6efe6;
    color: #342a22;
}

QWidget {
    background: #f6efe6;
    color: #342a22;
}

QLabel {
    background: transparent;
    color: #342a22;
}

QLabel#summaryLabel {
    background: #fff8ef;
    border: 1px solid #ead8c3;
    border-radius: 8px;
    color: #3c2b1e;
    font-size: 16px;
    font-weight: 700;
    padding: 8px 10px;
    margin: 4px 2px 8px 2px;
}

QLabel#reasonLabel {
    color: #9a5b2b;
    font-size: 13px;
    padding: 0 4px 8px 4px;
}

QLabel#emptyLabel {
    background: #fff8ef;
    border: 1px dashed #dcc6ad;
    border-radius: 8px;
    color: #7a6654;
    font-size: 14px;
    padding: 18px;
}

QLabel#cardTitle {
    color: #2f241c;
    font-size: 15px;
    font-weight: 700;
}

QLabel#cardDetail {
    color: #6a5848;
    font-size: 13px;
    line-height: 140%;
}

QLabel#fieldValue {
    color: #3c2b1e;
    font-size: 14px;
    font-weight: 600;
}

QFrame#optionCard {
    background: #fffaf3;
    border: 1px solid #e4d4c3;
    border-radius: 8px;
}

QFrame#optionCard:disabled {
    background: #f3ece4;
    border-color: #ded2c6;
}

QPushButton {
    background: #d8772d;
    border: 1px solid #c76722;
    border-radius: 7px;
    color: #ffffff;
    font-size: 14px;
    font-weight: 700;
    min-height: 32px;
    padding: 6px 16px;
}

QPushButton:hover {
    background: #c96824;
}

QPushButton:pressed {
    background: #ad581d;
}

QPushButton:disabled {
    background: #eee7df;
    border: 1px solid #d8cfc5;
    color: #978a7e;
}

QPushButton#secondaryButton {
    background: #fffaf3;
    border: 1px solid #d6c2ac;
    color: #6b4b35;
}

QPushButton#secondaryButton:hover {
    background: #f5e7d6;
}

QPushButton#dangerButton {
    background: #fff2ed;
    border: 1px solid #d89a82;
    color: #b1421f;
}

QPushButton#dangerButton:hover {
    background: #ffe3d8;
}

QGroupBox {
    background: #fff8ef;
    border: 1px solid #e1cfbc;
    border-radius: 8px;
    color: #3c2b1e;
    font-size: 15px;
    font-weight: 700;
    margin-top: 14px;
    padding: 16px 12px 12px 12px;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 12px;
    padding: 0 6px;
    background: #f6efe6;
}

QCheckBox {
    color: #3c2b1e;
    font-size: 14px;
    spacing: 8px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 1px solid #cdb79d;
    border-radius: 4px;
    background: #fffaf3;
}

QCheckBox::indicator:checked {
    background: #d8772d;
    border-color: #c76722;
}

QComboBox {
    background: #fffaf3;
    border: 1px solid #d6c2ac;
    border-radius: 7px;
    color: #3c2b1e;
    font-size: 14px;
    min-height: 32px;
    padding: 4px 28px 4px 10px;
}

QComboBox:hover {
    background: #fff4e7;
}

QComboBox::drop-down {
    border: none;
    width: 24px;
}

QComboBox QAbstractItemView {
    background: #fffaf3;
    border: 1px solid #d6c2ac;
    color: #3c2b1e;
    selection-background-color: #f3d6bd;
    selection-color: #2f241c;
}

QScrollArea {
    background: transparent;
    border: none;
}

QScrollArea > QWidget > QWidget {
    background: #f6efe6;
}

QScrollBar:vertical {
    background: transparent;
    width: 10px;
    margin: 2px 0;
}

QScrollBar::handle:vertical {
    background: #cab69f;
    border-radius: 5px;
    min-height: 28px;
}

QScrollBar::handle:vertical:hover {
    background: #b99d80;
}

QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical,
QScrollBar::add-page:vertical,
QScrollBar::sub-page:vertical {
    background: transparent;
    border: none;
    height: 0;
}

QScrollBar:horizontal {
    background: transparent;
    height: 10px;
    margin: 0 2px;
}

QScrollBar::handle:horizontal {
    background: #cab69f;
    border-radius: 5px;
    min-width: 28px;
}

QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal,
QScrollBar::add-page:horizontal,
QScrollBar::sub-page:horizontal {
    background: transparent;
    border: none;
    width: 0;
}

QTabWidget::pane {
    border: 1px solid #e1cfbc;
    border-radius: 8px;
    background: #fff8ef;
    top: -1px;
}

QTabBar::tab {
    background: #ead9c5;
    border: 1px solid #d8c3ab;
    border-bottom: none;
    border-top-left-radius: 7px;
    border-top-right-radius: 7px;
    color: #6b4b35;
    font-weight: 700;
    min-width: 72px;
    padding: 7px 14px;
}

QTabBar::tab:selected {
    background: #fff8ef;
    color: #3c2b1e;
}

QTabBar::tab:!selected:hover {
    background: #f3e4d3;
}
"""

CONTEXT_MENU_STYLE = """
QMenu {
    background: #fff8ef;
    border: 1px solid #d6c2ac;
    border-radius: 8px;
    color: #3c2b1e;
    font-size: 15px;
    font-weight: 700;
    padding: 6px;
}

QMenu::item {
    background: transparent;
    border-radius: 6px;
    padding: 7px 28px 7px 18px;
}

QMenu::item:selected {
    background: #f3d6bd;
    color: #2f241c;
}

QMenu::separator {
    background: #dfc8b0;
    height: 1px;
    margin: 6px 6px;
}
"""
