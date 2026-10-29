"""
VFD Parameter Screen for DLP KUMAR VFD HMI.
ISA-101 High-Performance SCADA Parameter Management for Fuji FRENIC-Mini C2.
Provides clean parameter inspection, safe modification with range checking,
and on-screen industrial touch numpad dialog.
"""
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QDialog, QLineEdit, QGridLayout
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
                background-color: #0c1017;
                border: 1px solid #3b82f6;
                border-radius: 8px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(8)
        
        # Header
        fcode = param_info.get('fuji_code') or param_info.get('id', '')
        lbl_title = QLabel(f"EDIT: {fcode} - {param_info.get('name', 'Parameter')}")
        lbl_title.setFont(QFont("Segoe UI", 10, QFont.Bold))
        lbl_title.setStyleSheet("color: #f1f5f9; border: none;")
        layout.addWidget(lbl_title)
        
        # Limits Info
        lbl_limits = QLabel(f"Allowed Range: {param_info.get('min')} to {param_info.get('max')} {param_info.get('unit')}")
        lbl_limits.setFont(QFont("Segoe UI", 8))
        lbl_limits.setStyleSheet("color: #64748b; border: none;")
        layout.addWidget(lbl_limits)
        
        # Input Box
        self.input_field = QLineEdit(str(current_val))
        self.input_field.setFixedHeight(42)
        self.input_field.setFont(QFont("Consolas", 18, QFont.Bold))
        self.input_field.setAlignment(Qt.AlignCenter)
        self.input_field.setStyleSheet("""
            QLineEdit {
                background-color: #090d13;
                color: #f8fafc;
                border: 1px solid #1e293b;
                border-radius: 5px;
            }
        """)
        layout.addWidget(self.input_field)
        
        # Numpad Grid
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
            btn.setFixedHeight(36)
            btn.setFont(QFont("Segoe UI", 11, QFont.Bold))
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #1e293b;
                    color: #f1f5f9;
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
        btn_cancel.setFixedHeight(38)
        btn_cancel.setFont(QFont("Segoe UI", 9, QFont.Bold))
        btn_cancel.setStyleSheet("""
            background-color: #1e293b; color: #94a3b8;
            border: 1px solid #334155; border-radius: 4px;
        """)
        btn_cancel.clicked.connect(self.reject)
        
        btn_confirm = QPushButton("APPLY SETTING")
        btn_confirm.setFixedHeight(38)
        btn_confirm.setFont(QFont("Segoe UI", 9, QFont.Bold))
        btn_confirm.setStyleSheet("""
            background-color: #2563eb; color: #ffffff;
            border: 1px solid #3b82f6; border-radius: 4px;
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
                self.input_field.setStyleSheet("background-color: #090d13; color: #ef4444; border: 1px solid #ef4444; border-radius: 5px;")
        except ValueError:
            self.input_field.setStyleSheet("background-color: #090d13; color: #ef4444; border: 1px solid #ef4444; border-radius: 5px;")


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
        btn_reload = QPushButton("↻  RELOAD DRIVE PARAMETERS")
        btn_reload.setFixedHeight(40)
        btn_reload.setFont(QFont("Segoe UI", 9, QFont.Bold))
        btn_reload.setStyleSheet("""
            QPushButton {
                background-color: #1e293b; color: #cbd5e1;
                border: 1px solid #334155; border-radius: 4px;
            }
            QPushButton:hover { background-color: #2563eb; color: #ffffff; border: 1px solid #3b82f6; }
        """)
        btn_reload.clicked.connect(self._reload_params)
        
        self.lbl_status = QLabel("PARAMETERS SYNCHRONIZED")
        self.lbl_status.setFont(QFont("Consolas", 9))
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
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        for param in params_list:
            card = QFrame()
            card.setFixedHeight(52)
            card.setStyleSheet("""
                QFrame {
                    background-color: #131923;
                    border: 1px solid #1e293b;
                    border-radius: 5px;
                }
            """)
            c_layout = QHBoxLayout(card)
            c_layout.setContentsMargins(12, 4, 12, 4)
            c_layout.setSpacing(10)
            
            # Param Fuji Code / ID Badge
            fcode = param.get("fuji_code") or param.get("id", "P00")
            lbl_id = QLabel(fcode)
            lbl_id.setFont(QFont("Consolas", 10, QFont.Bold))
            lbl_id.setAlignment(Qt.AlignCenter)
            lbl_id.setFixedSize(50, 26)
            lbl_id.setStyleSheet("""
                color: #93c5fd;
                background-color: #090d13;
                border: 1px solid #1e293b;
                border-radius: 3px;
            """)
            
            # Name & Reg
            name_box = QVBoxLayout()
            name_box.setSpacing(1)
            lbl_name = QLabel(param.get("name", "Unknown"))
            lbl_name.setFont(QFont("Segoe UI", 9, QFont.Bold))
            lbl_name.setStyleSheet("color: #f1f5f9; border: none;")
            
            hex_reg = param.get("hex_register", f"0x{param.get('register', 0):04X}")
            dec_reg = param.get("register", 0)
            lbl_sub = QLabel(f"Modbus: {hex_reg} (Dec: {dec_reg}) | Limits: {param.get('min')} - {param.get('max')} {param.get('unit')}")
            lbl_sub.setFont(QFont("Consolas", 7))
            lbl_sub.setStyleSheet("color: #64748b; border: none;")
            
            name_box.addWidget(lbl_name)
            name_box.addWidget(lbl_sub)
            
            # Value Pill
            lbl_val = QLabel(f"{param.get('value')} {param.get('unit')}")
            lbl_val.setFont(QFont("Consolas", 12, QFont.Bold))
            lbl_val.setStyleSheet("color: #f8fafc; border: none; min-width: 90px;")
            lbl_val.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            
            # Edit Button
            btn_edit = QPushButton("EDIT")
            btn_edit.setFixedSize(62, 32)
            btn_edit.setFont(QFont("Segoe UI", 8, QFont.Bold))
            btn_edit.setStyleSheet("""
                QPushButton {
                    background-color: #1e293b; color: #cbd5e1;
                    border: 1px solid #334155; border-radius: 4px;
                }
                QPushButton:hover { background-color: #2563eb; color: #ffffff; border: 1px solid #3b82f6; }
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
