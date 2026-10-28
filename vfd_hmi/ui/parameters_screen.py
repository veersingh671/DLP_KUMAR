"""
VFD Parameter Screen for DLP KUMAR VFD HMI.
Provides parameter inspection and safe modification with range checking.
Includes on-screen touch editing dialog.
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QDialog, QLineEdit
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from ui.components import BaseScreen

class TouchEditDialog(QDialog):
    """
    On-screen touch numpad dialog for modifying parameters safely on touchscreens.
    """
    def __init__(self, param_info, current_val, parent=None):
        super().__init__(parent)
        self.param = param_info
        self.setFixedSize(360, 340)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setStyleSheet("""
            QDialog {
                background-color: #0f1624;
                border: 2px solid #ff7a00;
                border-radius: 10px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(8)
        
        # Header
        lbl_title = QLabel(f"EDIT: {param_info.get('name', 'Parameter')}")
        lbl_title.setFont(QFont("Segoe UI", 11, QFont.Bold))
        lbl_title.setStyleSheet("color: #ff7a00; border: none;")
        layout.addWidget(lbl_title)
        
        # Limits Info
        lbl_limits = QLabel(f"Range: {param_info.get('min')} to {param_info.get('max')} {param_info.get('unit')}")
        lbl_limits.setFont(QFont("Segoe UI", 9))
        lbl_limits.setStyleSheet("color: #64748b; border: none;")
        layout.addWidget(lbl_limits)
        
        # Input Box
        self.input_field = QLineEdit(str(current_val))
        self.input_field.setFixedHeight(44)
        self.input_field.setFont(QFont("Consolas", 18, QFont.Bold))
        self.input_field.setAlignment(Qt.AlignCenter)
        self.input_field.setStyleSheet("""
            QLineEdit {
                background-color: #0b0f19;
                color: #f8fafc;
                border: 1px solid #334155;
                border-radius: 6px;
            }
        """)
        layout.addWidget(self.input_field)
        
        # Numpad Grid
        from PyQt5.QtWidgets import QGridLayout
        grid = QGridLayout()
        grid.setSpacing(6)
        
        buttons = [
            ("7", 0, 0), ("8", 0, 1), ("9", 0, 2),
            ("4", 1, 0), ("5", 1, 1), ("6", 1, 2),
            ("1", 2, 0), ("2", 2, 1), ("3", 2, 2),
            (".", 3, 0), ("0", 3, 1), ("DEL", 3, 2)
        ]
        
        for text, r, c in buttons:
            btn = QPushButton(text)
            btn.setFixedHeight(38)
            btn.setFont(QFont("Segoe UI", 12, QFont.Bold))
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #1e293b;
                    color: #f8fafc;
                    border: 1px solid #334155;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #334155;
                }
            """)
            btn.clicked.connect(lambda checked, t=text: self._on_numpad_press(t))
            grid.addWidget(btn, r, c)
            
        layout.addLayout(grid)
        
        # Action Buttons (Cancel / Confirm)
        act_row = QHBoxLayout()
        btn_cancel = QPushButton("CANCEL")
        btn_cancel.setFixedHeight(42)
        btn_cancel.setFont(QFont("Segoe UI", 10, QFont.Bold))
        btn_cancel.setStyleSheet("""
            background-color: #1e293b; color: #94a3b8;
            border: 1px solid #334155; border-radius: 6px;
        """)
        btn_cancel.clicked.connect(self.reject)
        
        btn_confirm = QPushButton("APPLY")
        btn_confirm.setFixedHeight(42)
        btn_confirm.setFont(QFont("Segoe UI", 10, QFont.Bold))
        btn_confirm.setStyleSheet("""
            background-color: #ff7a00; color: #ffffff;
            border: 1px solid #ea580c; border-radius: 6px;
        """)
        btn_confirm.clicked.connect(self._on_confirm)
        
        act_row.addWidget(btn_cancel)
        act_row.addWidget(btn_confirm)
        layout.addLayout(act_row)
        
        self.result_value = current_val

    def _on_numpad_press(self, key):
        cur = self.input_field.text()
        if key == "DEL":
            self.input_field.setText(cur[:-1])
        elif key == ".":
            if "." not in cur:
                self.input_field.setText(cur + ".")
        else:
            self.input_field.setText(cur + key)

    def _on_confirm(self):
        try:
            val = float(self.input_field.text())
            p_min = float(self.param.get("min", 0.0))
            p_max = float(self.param.get("max", 100.0))
            if p_min <= val <= p_max:
                self.result_value = val
                self.accept()
            else:
                self.input_field.setStyleSheet("background-color: #0b0f19; color: #ef4444; border: 2px solid #ef4444; border-radius: 6px;")
        except ValueError:
            self.input_field.setStyleSheet("background-color: #0b0f19; color: #ef4444; border: 2px solid #ef4444; border-radius: 6px;")


class ParametersScreen(BaseScreen):
    def __init__(self, controller=None, parent=None):
        super().__init__(controller, parent)
        
        # Scroll Area for parameter rows
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: transparent; }")
        
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_layout.setSpacing(6)
        
        scroll.setWidget(self.scroll_content)
        self.layout.addWidget(scroll)
        
        # Bottom Controls
        bottom_row = QHBoxLayout()
        btn_reload = QPushButton("↻  RELOAD FROM VFD")
        btn_reload.setFixedHeight(46)
        btn_reload.setFont(QFont("Segoe UI", 10, QFont.Bold))
        btn_reload.setStyleSheet("""
            QPushButton {
                background-color: #1e293b; color: #38bdf8;
                border: 1px solid #334155; border-radius: 6px;
            }
            QPushButton:hover { background-color: #334155; }
        """)
        btn_reload.clicked.connect(self._reload_params)
        
        self.lbl_status = QLabel("PARAMETERS READY")
        self.lbl_status.setFont(QFont("Segoe UI", 9))
        self.lbl_status.setStyleSheet("color: #64748b;")
        
        bottom_row.addWidget(btn_reload)
        bottom_row.addStretch()
        bottom_row.addWidget(self.lbl_status)
        self.layout.addLayout(bottom_row)
        
        # Populate initial
        if self.controller:
            self.controller.parameters_updated.connect(self.populate_parameters)
            self.populate_parameters(self.controller.parameters)

    def populate_parameters(self, params_list):
        # Clear existing
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        for param in params_list:
            card = QFrame()
            card.setFixedHeight(56)
            card.setStyleSheet("""
                QFrame {
                    background-color: #121824;
                    border: 1px solid #1e293b;
                    border-radius: 6px;
                }
            """)
            c_layout = QHBoxLayout(card)
            c_layout.setContentsMargins(14, 4, 14, 4)
            c_layout.setSpacing(10)
            
            # Param ID
            lbl_id = QLabel(param.get("id", "P00"))
            lbl_id.setFont(QFont("Consolas", 11, QFont.Bold))
            lbl_id.setStyleSheet("color: #ff7a00; border: none; min-width: 38px;")
            
            # Name & Reg
            name_box = QVBoxLayout()
            lbl_name = QLabel(param.get("name", "Unknown"))
            lbl_name.setFont(QFont("Segoe UI", 10, QFont.Bold))
            lbl_name.setStyleSheet("color: #f8fafc; border: none;")
            
            lbl_sub = QLabel(f"Reg: {param.get('register')} | Range: {param.get('min')}..{param.get('max')} {param.get('unit')}")
            lbl_sub.setFont(QFont("Segoe UI", 8))
            lbl_sub.setStyleSheet("color: #64748b; border: none;")
            
            name_box.addWidget(lbl_name)
            name_box.addWidget(lbl_sub)
            
            # Value Pill
            lbl_val = QLabel(f"{param.get('value')} {param.get('unit')}")
            lbl_val.setFont(QFont("Consolas", 13, QFont.Bold))
            lbl_val.setStyleSheet("color: #38bdf8; border: none; min-width: 90px;")
            lbl_val.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            
            # Edit Button
            btn_edit = QPushButton("EDIT")
            btn_edit.setFixedSize(65, 34)
            btn_edit.setFont(QFont("Segoe UI", 9, QFont.Bold))
            btn_edit.setStyleSheet("""
                QPushButton {
                    background-color: #1e293b; color: #f8fafc;
                    border: 1px solid #334155; border-radius: 4px;
                }
                QPushButton:hover { background-color: #ff7a00; color: #ffffff; border: 1px solid #ea580c; }
            """)
            btn_edit.clicked.connect(lambda checked, p=param: self._edit_param(p))
            
            c_layout.addWidget(lbl_id)
            c_layout.addLayout(name_box)
            c_layout.addStretch()
            c_layout.addWidget(lbl_val)
            c_layout.addWidget(btn_edit)
            
            self.scroll_layout.addWidget(card)
            
        self.scroll_layout.addStretch()

    def _edit_param(self, param):
        dialog = TouchEditDialog(param, param.get("value", 0.0), self)
        if dialog.exec_() == QDialog.Accepted:
            new_val = dialog.result_value
            if self.controller:
                success, msg = self.controller.update_parameter(param.get("id"), new_val)
                self.lbl_status.setText(msg.upper())
                self.lbl_status.setStyleSheet("color: #10b981;" if success else "color: #ef4444;")

    def _reload_params(self):
        if self.controller:
            self.populate_parameters(self.controller.parameters)
            self.lbl_status.setText("RELOADED SUCCESSFULLY")
            self.lbl_status.setStyleSheet("color: #10b981;")
