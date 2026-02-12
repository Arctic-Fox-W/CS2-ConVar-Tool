# Copyright 2026 Zero RCON Tool Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from typing import Optional
from rcon.source import Client
import os
import json
import re
import time
import time
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QLineEdit, QSpinBox, QDoubleSpinBox, QPushButton, QPlainTextEdit, QTabWidget, QTableWidget, QTableWidgetItem, QTreeWidget, QTreeWidgetItem, QSplitter, QFileDialog
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon

def _resource_path(name: str) -> str:
    base = getattr(sys, "_MEIPASS", os.path.dirname(__file__))
    return os.path.join(base, name)

class RCONClient:
    def __init__(self, host: str, port: int, password: str, timeout: float = 5.0):
        self.host = host
        self.port = port
        self.password = password
        self.timeout = timeout
        self.client: Optional[Client] = None
        self.authenticated = False

    def connect(self) -> bool:
        try:
            self.client = Client(self.host, self.port, passwd=self.password)
            self.client.__enter__()
            self.authenticated = True
            return True
        except Exception as e:
            self.disconnect()
            raise ConnectionError(f"RCON authentication failed: {e}")

    def disconnect(self):
        if self.client:
            try:
                self.client.__exit__(None, None, None)
            finally:
                self.client = None
        self.authenticated = False

    def execute(self, command: str, timeout: Optional[float] = None) -> str:
        if not self.authenticated or not self.client:
            raise PermissionError("Not authenticated. Call connect() first.")
        result = self.client.run(command)
        if isinstance(result, (bytes, bytearray)):
            return result.decode('utf-8', errors='ignore').strip()
        return str(result).strip()

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

if __name__ == "__main__":
    class RCONWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("ZeRo社区RCON配置工具(Develop By: Arctic_Fox)")
            try:
                self.setWindowIcon(QIcon(_resource_path("logo.ico")))
            except Exception:
                try:
                    self.setWindowIcon(QIcon(_resource_path("logo.jpg")))
                except Exception:
                    pass
            self._ui_applied = False
            self.client: Optional[RCONClient] = None
            central = QWidget()
            self.setCentralWidget(central)
            layout = QVBoxLayout(central)
            row1 = QHBoxLayout()
            self.host_edit = QLineEdit("202.189.12.174")
            self.port_spin = QSpinBox()
            self.port_spin.setRange(1, 65535)
            self.port_spin.setValue(27015)
            self.pass_edit = QLineEdit()
            self.pass_edit.setEchoMode(QLineEdit.Password)
            row1.addWidget(QLabel("Host"))
            row1.addWidget(self.host_edit)
            row1.addWidget(QLabel("Port"))
            row1.addWidget(self.port_spin)
            row1.addWidget(QLabel("Password"))
            row1.addWidget(self.pass_edit)
            layout.addLayout(row1)
            row2 = QHBoxLayout()
            self.connect_btn = QPushButton("连接")
            self.disconnect_btn = QPushButton("断开")
            self.disconnect_btn.setEnabled(False)
            self.status_lbl = QLabel("未连接")
            row2.addWidget(self.connect_btn)
            row2.addWidget(self.disconnect_btn)
            row2.addWidget(self.status_lbl)
            layout.addLayout(row2)
            self.tabs = QTabWidget()
            layout.addWidget(self.tabs)
            console_tab = QWidget()
            console_layout = QVBoxLayout(console_tab)
            row3 = QHBoxLayout()
            self.cmd_edit = QLineEdit()
            self.cmd_edit.setPlaceholderText("输入命令，如 status 或 mp_restartgame 1")
            self.send_btn = QPushButton("发送")
            self.send_btn.setEnabled(False)
            row3.addWidget(self.cmd_edit)
            row3.addWidget(self.send_btn)
            self.console_splitter = QSplitter()
            left_panel = QWidget()
            left_layout = QVBoxLayout(left_panel)
            self.restart_btn = QPushButton("重启回合")
            self.cheats_toggle_btn = QPushButton("开关作弊")
            self.warmup_start_btn = QPushButton("开始热身")
            self.warmup_end_btn = QPushButton("结束热身")
            self.pause_btn = QPushButton("暂停比赛")
            self.unpause_btn = QPushButton("继续比赛")
            self.get_map_btn = QPushButton("获取当前地图")
            self.bot_add_btn = QPushButton("增加Bot")
            self.bot_kick_btn = QPushButton("踢出Bot")
            self.bot_dontshoot_btn = QPushButton("停止开枪")
            self.bot_stop_btn = QPushButton("停止移动")
            self.bot_freeze_btn = QPushButton("冻结")
            self.timescale_spin = QDoubleSpinBox()
            self.timescale_spin.setRange(0.5, 5.0)
            self.timescale_spin.setSingleStep(0.5)
            self.timescale_spin.setDecimals(1)
            self.timescale_spin.setValue(1.0)
            self.ts_minus_btn = QPushButton("-")
            self.ts_plus_btn = QPushButton("+")
            self.ts_apply_btn = QPushButton("加速")
            self.ts_reset_btn = QPushButton("恢复")
            for b in [self.restart_btn, self.cheats_toggle_btn, self.warmup_start_btn, self.warmup_end_btn, self.pause_btn, self.unpause_btn, self.get_map_btn, self.bot_add_btn, self.bot_kick_btn, self.bot_dontshoot_btn, self.bot_stop_btn, self.bot_freeze_btn, self.ts_minus_btn, self.ts_plus_btn, self.ts_apply_btn, self.ts_reset_btn]:
                b.setEnabled(False)
            self.timescale_spin.setEnabled(False)
            grid = QGridLayout()
            for b in [self.restart_btn, self.cheats_toggle_btn, self.warmup_start_btn, self.warmup_end_btn, self.pause_btn, self.unpause_btn, self.get_map_btn, self.bot_add_btn, self.bot_kick_btn, self.bot_dontshoot_btn, self.bot_stop_btn, self.bot_freeze_btn]:
                b.setMaximumWidth(120)
            grid.setVerticalSpacing(max(12, grid.verticalSpacing() * 2 if grid.verticalSpacing() > 0 else 16))
            grid.addWidget(self.restart_btn, 0, 0)
            grid.addWidget(self.cheats_toggle_btn, 0, 1)
            grid.addWidget(self.warmup_start_btn, 1, 0)
            grid.addWidget(self.warmup_end_btn, 1, 1)
            grid.addWidget(self.pause_btn, 2, 0)
            grid.addWidget(self.unpause_btn, 2, 1)
            grid.addWidget(self.get_map_btn, 3, 0)
            grid.addWidget(self.bot_add_btn, 3, 1)
            grid.addWidget(self.bot_kick_btn, 4, 0)
            grid.addWidget(self.bot_dontshoot_btn, 4, 1)
            grid.addWidget(self.bot_stop_btn, 5, 0)
            grid.addWidget(self.bot_freeze_btn, 5, 1)
            left_layout.addLayout(grid)
            left_layout.setSpacing(max(12, left_layout.spacing() * 2 if left_layout.spacing() > 0 else 16))
            speed_row = QHBoxLayout()
            speed_row.addWidget(self.ts_minus_btn)
            speed_row.addWidget(self.timescale_spin)
            speed_row.addWidget(self.ts_plus_btn)
            speed_row.addWidget(self.ts_apply_btn)
            speed_row.addWidget(self.ts_reset_btn)
            left_layout.addLayout(speed_row)
            right_panel = QWidget()
            right_layout = QVBoxLayout(right_panel)
            right_layout.addLayout(row3)
            self.output = QPlainTextEdit()
            self.output.setReadOnly(True)
            right_layout.addWidget(self.output)
            self.console_splitter.addWidget(left_panel)
            self.console_splitter.addWidget(right_panel)
            self.console_splitter.setStretchFactor(0, 1)
            self.console_splitter.setStretchFactor(1, 3)
            self.console_splitter.setSizes([275, 825])
            console_layout.addWidget(self.console_splitter)
            self.tabs.addTab(console_tab, "控制台")
            convar_tab = QWidget()
            convar_layout = QVBoxLayout(convar_tab)
            top_row = QHBoxLayout()
            self.add_row_btn = QPushButton("新增一行")
            self.fetch_all_btn = QPushButton("一键获取")
            self.save_btn = QPushButton("保存配置")
            self.load_btn = QPushButton("加载配置")
            self.save_initial_btn = QPushButton("保存初始值")
            top_row.addWidget(self.add_row_btn)
            top_row.addWidget(self.fetch_all_btn)
            top_row.addWidget(self.save_btn)
            top_row.addWidget(self.save_initial_btn)
            top_row.addWidget(self.load_btn)
            top_row.addStretch(1)
            convar_layout.addLayout(top_row)
            self.splitter = QSplitter()
            self.tree = QTreeWidget()
            self.tree.setHeaderLabels(["ZeRo社区RCON"])
            self.root_all = QTreeWidgetItem(["全部"])
            self.root_all.setFlags(self.root_all.flags() & ~Qt.ItemIsEditable)
            self.tree.addTopLevelItem(self.root_all)
            self.tree.setCurrentItem(self.root_all)
            self.table = QTableWidget(0, 7)
            self.table.setHorizontalHeaderLabels(["ConVar 名称", "中文名", "初始值", "当前值", "期望值", "确认", "获取当前值"])
            self.table.setEditTriggers(self.table.EditTrigger.AllEditTriggers)
            self.table.setSortingEnabled(False)
            self.splitter.addWidget(self.tree)
            self.splitter.addWidget(self.table)
            self.tree.setMinimumWidth(275)
            self.splitter.setStretchFactor(0, 1)
            self.splitter.setStretchFactor(1, 3)
            self.splitter.setSizes([275, 825])
            convar_layout.addWidget(self.splitter)
            self.tabs.addTab(convar_tab, "ConVar")
            sb = self.statusBar()
            self.status_ip = QLabel("IP: -")
            self.status_port = QLabel("Port: -")
            self.status_players = QLabel("在线: -")
            self.status_map = QLabel("地图: -")
            sb.addPermanentWidget(self.status_ip)
            sb.addPermanentWidget(self.status_port)
            sb.addPermanentWidget(self.status_players)
            sb.addPermanentWidget(self.status_map)
            self.status_timer = QTimer(self)
            self.status_timer.setInterval(5000)
            self.status_timer.timeout.connect(self.on_status_timer)
            base_dir = os.path.dirname(sys.executable) if getattr(sys, "frozen", False) else os.path.dirname(os.path.abspath(__file__))
            self.config_path = os.path.join(base_dir, "convars_config.json")
            self.connect_btn.clicked.connect(self.on_connect)
            self.disconnect_btn.clicked.connect(self.on_disconnect)
            self.send_btn.clicked.connect(self.on_send)
            self.restart_btn.clicked.connect(self.on_cmd_restart_round)
            self.cheats_toggle_btn.clicked.connect(self.on_cmd_toggle_cheats)
            self.warmup_start_btn.clicked.connect(self.on_cmd_warmup_start)
            self.warmup_end_btn.clicked.connect(self.on_cmd_warmup_end)
            self.pause_btn.clicked.connect(self.on_cmd_pause_match)
            self.unpause_btn.clicked.connect(self.on_cmd_unpause_match)
            self.get_map_btn.clicked.connect(self.on_cmd_get_current_map)
            self.bot_add_btn.clicked.connect(self.on_cmd_bot_add)
            self.bot_kick_btn.clicked.connect(self.on_cmd_bot_kick)
            self.bot_dontshoot_btn.clicked.connect(self.on_cmd_bot_dont_shoot)
            self.bot_stop_btn.clicked.connect(self.on_cmd_bot_stop_move)
            self.bot_freeze_btn.clicked.connect(self.on_cmd_bot_freeze)
            self.ts_minus_btn.clicked.connect(self.on_ts_minus)
            self.ts_plus_btn.clicked.connect(self.on_ts_plus)
            self.ts_apply_btn.clicked.connect(self.on_ts_apply)
            self.ts_reset_btn.clicked.connect(self.on_ts_reset)
            self.add_row_btn.clicked.connect(self.on_add_row)
            self.fetch_all_btn.clicked.connect(self.on_fetch_all)
            self.save_btn.clicked.connect(self.on_save_config)
            self.save_initial_btn.clicked.connect(self.on_save_initials)
            self.load_btn.clicked.connect(self.on_load_config)
            self.tree.currentItemChanged.connect(self.on_tree_selection_changed)
            self.search_edit = QLineEdit()
            self.search_edit.setPlaceholderText("搜索 ConVar 名称或中文名")
            top_row.addWidget(self.search_edit)
            self.search_edit.textChanged.connect(self.on_search_changed)
            self.import_btn = QPushButton("导入 ConVars")
            top_row.insertWidget(2, self.import_btn)
            self.add_group_btn = QPushButton("新增分级")
            self.add_weapon_btn = QPushButton("新增武器")
            self.delete_node_btn = QPushButton("删除选中")
            top_row.insertWidget(2, self.add_group_btn)
            top_row.insertWidget(3, self.add_weapon_btn)
            top_row.insertWidget(4, self.delete_node_btn)
            self.add_group_btn.clicked.connect(self.on_add_group)
            self.add_weapon_btn.clicked.connect(self.on_add_weapon)
            self.delete_node_btn.clicked.connect(self.on_delete_node)
            self.import_btn.clicked.connect(self.on_import_convars)
            self.table.cellChanged.connect(self.on_table_cell_changed)
            self.config_path_display = QLineEdit(self.config_path)
            self.config_path_display.setReadOnly(True)
            top_row.addWidget(self.config_path_display)
            self.choose_config_btn = QPushButton("选择配置")
            self.choose_config_btn.clicked.connect(self.on_choose_config)
            top_row.addWidget(self.choose_config_btn)
            self.load_config()
        def on_connect(self):
            host = self.host_edit.text().strip()
            port = int(self.port_spin.value())
            password = self.pass_edit.text()
            try:
                self.client = RCONClient(host, port, password)
                self.client.connect()
                self.status_lbl.setText("已连接")
                self.connect_btn.setEnabled(False)
                self.disconnect_btn.setEnabled(True)
                self.send_btn.setEnabled(True)
                self.restart_btn.setEnabled(True)
                self.cheats_toggle_btn.setEnabled(True)
                self.warmup_start_btn.setEnabled(True)
                self.warmup_end_btn.setEnabled(True)
                self.pause_btn.setEnabled(True)
                self.unpause_btn.setEnabled(True)
                self.get_map_btn.setEnabled(True)
                self.bot_add_btn.setEnabled(True)
                self.bot_kick_btn.setEnabled(True)
                self.bot_dontshoot_btn.setEnabled(True)
                self.bot_stop_btn.setEnabled(True)
                self.bot_freeze_btn.setEnabled(True)
                self.ts_minus_btn.setEnabled(True)
                self.ts_plus_btn.setEnabled(True)
                self.ts_apply_btn.setEnabled(True)
                self.ts_reset_btn.setEnabled(True)
                self.timescale_spin.setEnabled(True)
                self.status_ip.setText(f"IP: {host}")
                self.status_port.setText(f"Port: {port}")
                self.refresh_status_bar()
                self.status_timer.start()
                self.output.appendPlainText("已连接到服务器")
            except Exception as e:
                self.client = None
                self.status_lbl.setText("连接失败")
                self.output.appendPlainText(str(e))
        def on_disconnect(self):
            if self.client:
                try:
                    self.client.disconnect()
                except Exception as e:
                    self.output.appendPlainText(str(e))
                self.client = None
            self.status_lbl.setText("未连接")
            self.connect_btn.setEnabled(True)
            self.disconnect_btn.setEnabled(False)
            self.send_btn.setEnabled(False)
            self.restart_btn.setEnabled(False)
            self.cheats_toggle_btn.setEnabled(False)
            self.warmup_start_btn.setEnabled(False)
            self.warmup_end_btn.setEnabled(False)
            self.pause_btn.setEnabled(False)
            self.unpause_btn.setEnabled(False)
            self.get_map_btn.setEnabled(False)
            self.bot_add_btn.setEnabled(False)
            self.bot_kick_btn.setEnabled(False)
            self.bot_dontshoot_btn.setEnabled(False)
            self.bot_stop_btn.setEnabled(False)
            self.bot_freeze_btn.setEnabled(False)
            self.ts_minus_btn.setEnabled(False)
            self.ts_plus_btn.setEnabled(False)
            self.ts_apply_btn.setEnabled(False)
            self.ts_reset_btn.setEnabled(False)
            self.timescale_spin.setEnabled(False)
            self.status_ip.setText("IP: -")
            self.status_port.setText("Port: -")
            self.status_players.setText("在线: -")
            self.status_map.setText("地图: -")
            if hasattr(self, "status_timer"):
                self.status_timer.stop()
            self.output.appendPlainText("已断开连接")
        def on_send(self):
            cmd = self.cmd_edit.text().strip()
            if not cmd or not self.client:
                return
            try:
                resp = self.client.execute(cmd)
                self.output.appendPlainText(f"$ {cmd}\n{resp or 'OK'}")
            except Exception as e:
                self.output.appendPlainText(f"$ {cmd}\n{str(e)}")
            self.cmd_edit.clear()
        def on_save_initials(self):
            self.table.blockSignals(True)
            try:
                for r in range(self.table.rowCount()):
                    cur_item = self.table.item(r, 3)
                    val = cur_item.text().strip() if cur_item and cur_item.text() else ""
                    init_item = self.table.item(r, 2)
                    if init_item is None:
                        init_item = QTableWidgetItem("")
                        init_item.setFlags(init_item.flags() & ~Qt.ItemIsEditable)
                        self.table.setItem(r, 2, init_item)
                    init_item.setText(val)
                self.save_config()
                self.output.appendPlainText("已将当前值保存为初始值")
            finally:
                self.table.blockSignals(False)
        def on_cmd_restart_round(self):
            if not self.client:
                return
            cmd = "mp_restartgame 1"
            try:
                resp = self.client.execute(cmd)
                self.output.appendPlainText(f"$ {cmd}\n{resp or 'OK'}")
            except Exception as e:
                self.output.appendPlainText(f"$ {cmd}\n{str(e)}")
        def on_cmd_toggle_cheats(self):
            if not self.client:
                return
            try:
                current = self.client.execute("sv_cheats")
                val = self._parse_convar_value("sv_cheats", current).lower()
                is_on = val in ("1", "true", "yes")
                new = "0" if is_on else "1"
                cmd = f"sv_cheats {new}"
                resp = self.client.execute(cmd)
                self.output.appendPlainText(f"$ {cmd}\n{resp or 'OK'}")
            except Exception as e:
                self.output.appendPlainText(str(e))
        def on_cmd_warmup_start(self):
            if not self.client:
                return
            cmd = "mp_warmup_start"
            try:
                resp = self.client.execute(cmd)
                self.output.appendPlainText(f"$ {cmd}\n{resp or 'OK'}")
            except Exception as e:
                self.output.appendPlainText(f"$ {cmd}\n{str(e)}")
        def on_cmd_warmup_end(self):
            if not self.client:
                return
            cmd = "mp_warmup_end"
            try:
                resp = self.client.execute(cmd)
                self.output.appendPlainText(f"$ {cmd}\n{resp or 'OK'}")
            except Exception as e:
                self.output.appendPlainText(f"$ {cmd}\n{str(e)}")
        def on_cmd_pause_match(self):
            if not self.client:
                return
            cmd = "mp_pause_match"
            try:
                resp = self.client.execute(cmd)
                self.output.appendPlainText(f"$ {cmd}\n{resp or 'OK'}")
            except Exception as e:
                self.output.appendPlainText(f"$ {cmd}\n{str(e)}")
        def on_cmd_unpause_match(self):
            if not self.client:
                return
            cmd = "mp_unpause_match"
            try:
                resp = self.client.execute(cmd)
                self.output.appendPlainText(f"$ {cmd}\n{resp or 'OK'}")
            except Exception as e:
                self.output.appendPlainText(f"$ {cmd}\n{str(e)}")
        def on_cmd_get_current_map(self):
            if not self.client:
                return
            cmd = "status"
            try:
                resp = self.client.execute(cmd)
                name = self._extract_map_name(resp)
                cur, mx = self._extract_player_counts(resp)
                if name:
                    self.output.appendPlainText(f"$ {cmd}\n当前地图: {name}")
                else:
                    self.output.appendPlainText(f"$ {cmd}\n未能解析当前地图名\n{resp}")
                if cur is not None:
                    if mx is not None:
                        self.status_players.setText(f"在线: {cur}/{mx}")
                    else:
                        self.status_players.setText(f"在线: {cur}")
                if name:
                    self.status_map.setText(f"地图: {name}")
            except Exception as e:
                self.output.appendPlainText(f"$ {cmd}\n{str(e)}")
        def on_ts_minus(self):
            v = self.timescale_spin.value()
            v = max(self.timescale_spin.minimum(), v - self.timescale_spin.singleStep())
            self.timescale_spin.setValue(v)
        def on_ts_plus(self):
            v = self.timescale_spin.value()
            v = min(self.timescale_spin.maximum(), v + self.timescale_spin.singleStep())
            self.timescale_spin.setValue(v)
        def on_ts_apply(self):
            if not self.client:
                return
            try:
                current = self.client.execute("sv_cheats")
                val = self._parse_convar_value("sv_cheats", current).lower()
                if val not in ("1", "true", "yes"):
                    self.client.execute("sv_cheats 1")
            except Exception:
                pass
            cmd = f"host_timescale {self.timescale_spin.value():.1f}"
            try:
                resp = self.client.execute(cmd)
                self.output.appendPlainText(f"$ {cmd}\n{resp or 'OK'}")
            except Exception as e:
                self.output.appendPlainText(f"$ {cmd}\n{str(e)}")
        def on_ts_reset(self):
            if not self.client:
                return
            cmd = "host_timescale 1"
            try:
                resp = self.client.execute(cmd)
                self.output.appendPlainText(f"$ {cmd}\n{resp or 'OK'}")
            except Exception as e:
                self.output.appendPlainText(f"$ {cmd}\n{str(e)}")
        def on_cmd_bot_add(self):
            if not self.client:
                return
            cmd = "bot_add"
            try:
                resp = self.client.execute(cmd)
                self.output.appendPlainText(f"$ {cmd}\n{resp or 'OK'}")
            except Exception as e:
                self.output.appendPlainText(f"$ {cmd}\n{str(e)}")
        def on_cmd_bot_kick(self):
            if not self.client:
                return
            cmd = "bot_kick"
            try:
                resp = self.client.execute(cmd)
                self.output.appendPlainText(f"$ {cmd}\n{resp or 'OK'}")
            except Exception as e:
                self.output.appendPlainText(f"$ {cmd}\n{str(e)}")
        def on_cmd_bot_dont_shoot(self):
            if not self.client:
                return
            try:
                current = self.client.execute("sv_cheats")
                val = self._parse_convar_value("sv_cheats", current).lower()
                if val not in ("1", "true", "yes"):
                    self.client.execute("sv_cheats 1")
            except Exception:
                pass
            cmd = "bot_dont_shoot 1"
            try:
                resp = self.client.execute(cmd)
                self.output.appendPlainText(f"$ {cmd}\n{resp or 'OK'}")
            except Exception as e:
                self.output.appendPlainText(f"$ {cmd}\n{str(e)}")
        def on_cmd_bot_stop_move(self):
            if not self.client:
                return
            try:
                current = self.client.execute("sv_cheats")
                val = self._parse_convar_value("sv_cheats", current).lower()
                if val not in ("1", "true", "yes"):
                    self.client.execute("sv_cheats 1")
            except Exception:
                pass
            cmd = "bot_stop 1"
            try:
                resp = self.client.execute(cmd)
                self.output.appendPlainText(f"$ {cmd}\n{resp or 'OK'}")
            except Exception as e:
                self.output.appendPlainText(f"$ {cmd}\n{str(e)}")
        def on_cmd_bot_freeze(self):
            if not self.client:
                return
            try:
                current = self.client.execute("sv_cheats")
                val = self._parse_convar_value("sv_cheats", current).lower()
                if val not in ("1", "true", "yes"):
                    self.client.execute("sv_cheats 1")
            except Exception:
                pass
            cmd = "bot_freeze 1"
            try:
                resp = self.client.execute(cmd)
                self.output.appendPlainText(f"$ {cmd}\n{resp or 'OK'}")
            except Exception as e:
                self.output.appendPlainText(f"$ {cmd}\n{str(e)}")
        def _extract_map_name(self, status_output: str) -> str:
            for ln in status_output.splitlines():
                m = re.search(r"(?i)loaded\s*spawngroup.*SV:\s*\[\s*\d+\s*:\s*([^\|\]]+)", ln)
                if m:
                    return m.group(1).strip()
                m2 = re.search(r"(?i)\bmap\s*:\s*([^\s]+)", ln)
                if m2:
                    return m2.group(1)
            return ""
        def _extract_player_counts(self, status_output: str):
            for ln in status_output.splitlines():
                if re.search(r"(?i)\bplayers?\b", ln):
                    m = re.search(r"(\d+)\s*/\s*(\d+)", ln)
                    if m:
                        return int(m.group(1)), int(m.group(2))
                    m2 = re.search(r"(?i)players?\s*:\s*(\d+)", ln)
                    if m2:
                        return int(m2.group(1)), None
                    m3 = re.search(r"(?i)\b(\d+)\s+players\b", ln)
                    if m3:
                        return int(m3.group(1)), None
            return None, None
        def refresh_status_bar(self):
            if not self.client:
                return
            try:
                resp = self.client.execute("status")
                name = self._extract_map_name(resp)
                cur, mx = self._extract_player_counts(resp)
                if name:
                    self.status_map.setText(f"地图: {name}")
                if cur is not None:
                    if mx is not None:
                        self.status_players.setText(f"在线: {cur}/{mx}")
                    else:
                        self.status_players.setText(f"在线: {cur}")
            except Exception:
                pass
        def on_status_timer(self):
            self.refresh_status_bar()
        def on_add_row(self):
            r = self.table.rowCount()
            self.table.insertRow(r)
            for c in range(5):
                item = QTableWidgetItem("")
                if c in (0, 1, 4):
                    item.setFlags(item.flags() | Qt.ItemIsEditable)
                else:
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                self.table.setItem(r, c, item)
            path = self._current_weapon_path()
            self.table.item(r, 0).setData(Qt.UserRole, path)
            btn = QPushButton("确认")
            btn.clicked.connect(self.on_confirm_row)
            self.table.setCellWidget(r, 5, btn)
            get_btn = QPushButton("获取当前值")
            get_btn.clicked.connect(self.on_fetch_row)
            self.table.setCellWidget(r, 6, get_btn)
        def on_table_cell_changed(self, row, column):
            if column != 0:
                return
            if not self.client:
                return
            name_item = self.table.item(row, 0)
            if not name_item:
                return
            name = name_item.text().strip()
            if not name:
                return
            try:
                resp = self.client.execute(name)
                val = self._parse_convar_value(name, resp)
                self.table.blockSignals(True)
                cur_item = self.table.item(row, 3)
                if cur_item is None:
                    cur_item = QTableWidgetItem("")
                    cur_item.setFlags(cur_item.flags() & ~Qt.ItemIsEditable)
                    self.table.setItem(row, 3, cur_item)
                cur_item.setText(val)
                init_item = self.table.item(row, 2)
                if init_item is None:
                    init_item = QTableWidgetItem("")
                    init_item.setFlags(init_item.flags() & ~Qt.ItemIsEditable)
                    self.table.setItem(row, 2, init_item)
                if not init_item.text().strip():
                    init_item.setText(val)
                zh_item = self.table.item(row, 1)
                if zh_item is None:
                    zh_item = QTableWidgetItem("")
                    self.table.setItem(row, 1, zh_item)
                if not zh_item.text().strip():
                    zh_item.setText(name)
            finally:
                self.table.blockSignals(False)
        def on_fetch_all(self):
            if not self.client:
                return
            self.fetch_all_btn.setEnabled(False)
            self.table.blockSignals(True)
            try:
                for r in range(self.table.rowCount()):
                    if self.table.isRowHidden(r):
                        continue
                    name_item = self.table.item(r, 0)
                    if not name_item:
                        continue
                    name = name_item.text().strip()
                    if not name:
                        continue
                    try:
                        resp = self.client.execute(name)
                    except Exception as e:
                        self.output.appendPlainText(str(e))
                        continue
                    val = self._parse_convar_value(name, resp)
                    cur_item = self.table.item(r, 3)
                    if cur_item is None:
                        cur_item = QTableWidgetItem("")
                        cur_item.setFlags(cur_item.flags() & ~Qt.ItemIsEditable)
                        self.table.setItem(r, 3, cur_item)
                    cur_item.setText(val)
                    init_item = self.table.item(r, 2)
                    if init_item is None:
                        init_item = QTableWidgetItem("")
                        init_item.setFlags(init_item.flags() & ~Qt.ItemIsEditable)
                        self.table.setItem(r, 2, init_item)
                    if not init_item.text().strip():
                        init_item.setText(val)
                    zh_item = self.table.item(r, 1)
                    if zh_item is None:
                        zh_item = QTableWidgetItem("")
                        self.table.setItem(r, 1, zh_item)
                    if not zh_item.text().strip():
                        zh_item.setText(name)
                    QApplication.processEvents()
                    time.sleep(0.1)
            finally:
                self.table.blockSignals(False)
                self.fetch_all_btn.setEnabled(True)
        def on_tree_selection_changed(self, current, previous):
            self.apply_filters()
        def on_search_changed(self, text):
            self.apply_filters()
        def apply_filters(self):
            selected = self.tree.currentItem()
            search = self.search_edit.text().strip().lower() if hasattr(self, "search_edit") else ""
            selected_path = ""
            if selected and selected is not self.root_all:
                if selected.parent() and selected.parent() is not self.root_all:
                    selected_path = f"{selected.parent().text(0)}|{selected.text(0)}"
                elif selected.parent() is self.root_all:
                    selected_path = f"{selected.text(0)}|"
            for r in range(self.table.rowCount()):
                name_item = self.table.item(r, 0)
                zh_item = self.table.item(r, 1)
                path = name_item.data(Qt.UserRole) if name_item else ""
                path_match = True
                if selected_path:
                    if selected_path.endswith("|"):
                        path_match = isinstance(path, str) and path.startswith(selected_path)
                    else:
                        path_match = isinstance(path, str) and path == selected_path
                name_text = name_item.text().lower() if name_item and name_item.text() else ""
                zh_text = zh_item.text().lower() if zh_item and zh_item.text() else ""
                search_match = True if not search else (search in name_text or search in zh_text)
                self.table.setRowHidden(r, not (path_match and search_match))
        def on_add_group(self):
            item = QTreeWidgetItem([ "新分级" ])
            item.setFlags(item.flags() | Qt.ItemIsEditable)
            item.setChildIndicatorPolicy(QTreeWidgetItem.DontShowIndicatorWhenChildless)
            self.root_all.addChild(item)
            self.tree.setCurrentItem(item)
        def on_add_weapon(self):
            sel = self.tree.currentItem()
            if not sel or sel is self.root_all:
                grp = QTreeWidgetItem([ "新分级" ])
                grp.setFlags(grp.flags() | Qt.ItemIsEditable)
                grp.setChildIndicatorPolicy(QTreeWidgetItem.DontShowIndicatorWhenChildless)
                self.root_all.addChild(grp)
                self.tree.setCurrentItem(grp)
                sel = grp
            parent = sel if sel.parent() is self.root_all or sel is self.root_all else sel.parent()
            if parent is self.root_all:
                parent = sel
            weapon = QTreeWidgetItem([ "新武器" ])
            weapon.setFlags(weapon.flags() | Qt.ItemIsEditable)
            parent.addChild(weapon)
            self.tree.setCurrentItem(weapon)
        def _current_weapon_path(self) -> str:
            sel = self.tree.currentItem()
            if not sel or sel is self.root_all:
                return ""
            if sel.parent() is self.root_all:
                return f"{sel.text(0)}|"
            else:
                grp = sel.parent()
                return f"{grp.text(0)}|{sel.text(0)}"
        def on_delete_node(self):
            rows = sorted({idx.row() for idx in self.table.selectedIndexes()}, reverse=True)
            if rows:
                self.table.blockSignals(True)
                try:
                    for r in rows:
                        self.table.removeRow(r)
                finally:
                    self.table.blockSignals(False)
                self.apply_filters()
                self.save_config()
                self.output.appendPlainText("已删除选中的表格行")
                return
            sel = self.tree.currentItem()
            if not sel or sel is self.root_all:
                self.output.appendPlainText("未选择可删除的分级或武器节点")
                return
            if sel.parent() is None:
                self.output.appendPlainText("未选择可删除的分级或武器节点")
                return
            path_prefix = ""
            is_group = sel.parent() is self.root_all
            if is_group:
                path_prefix = f"{sel.text(0)}|"
            else:
                path_prefix = f"{sel.parent().text(0)}|{sel.text(0)}"
            self.table.blockSignals(True)
            try:
                for r in range(self.table.rowCount() - 1, -1, -1):
                    name_item = self.table.item(r, 0)
                    p = name_item.data(Qt.UserRole) if name_item else ""
                    if isinstance(p, str):
                        if is_group and p.startswith(path_prefix):
                            self.table.removeRow(r)
                        elif not is_group and p == path_prefix:
                            self.table.removeRow(r)
            finally:
                self.table.blockSignals(False)
            parent = sel.parent()
            if parent:
                parent.removeChild(sel)
            self.apply_filters()
            self.save_config()
            self.output.appendPlainText("已删除选中的树节点及其关联的属性行")
        def on_fetch_row(self):
            if not self.client:
                return
            sender = self.sender()
            target_row = -1
            for r in range(self.table.rowCount()):
                w = self.table.cellWidget(r, 6)
                if w is sender:
                    target_row = r
                    break
            if target_row < 0:
                return
            name_item = self.table.item(target_row, 0)
            if not name_item:
                return
            name = name_item.text().strip()
            if not name:
                return
            try:
                resp = self.client.execute(name)
                val = self._parse_convar_value(name, resp)
                self.table.blockSignals(True)
                cur_item = self.table.item(target_row, 3)
                if cur_item is None:
                    cur_item = QTableWidgetItem("")
                    cur_item.setFlags(cur_item.flags() & ~Qt.ItemIsEditable)
                    self.table.setItem(target_row, 3, cur_item)
                cur_item.setText(val)
                init_item = self.table.item(target_row, 2)
                if init_item is None:
                    init_item = QTableWidgetItem("")
                    init_item.setFlags(init_item.flags() & ~Qt.ItemIsEditable)
                    self.table.setItem(target_row, 2, init_item)
                if not init_item.text().strip():
                    init_item.setText(val)
                zh_item = self.table.item(target_row, 1)
                if zh_item is None:
                    zh_item = QTableWidgetItem("")
                    self.table.setItem(target_row, 1, zh_item)
                if not zh_item.text().strip():
                    zh_item.setText(name)
            finally:
                self.table.blockSignals(False)
        def on_confirm_row(self):
            if not self.client:
                return
            sender = self.sender()
            target_row = -1
            for r in range(self.table.rowCount()):
                w = self.table.cellWidget(r, 5)
                if w is sender:
                    target_row = r
                    break
            if target_row < 0:
                return
            name_item = self.table.item(target_row, 0)
            desired_item = self.table.item(target_row, 4)
            if not name_item or not desired_item:
                return
            name = name_item.text().strip()
            desired = desired_item.text().strip()
            if not name or not desired:
                return
            cmd = f"{name} {desired}"
            try:
                resp = self.client.execute(cmd)
                self.output.appendPlainText(f"$ {cmd}\n{resp or 'OK'}")
                refresh = self.client.execute(name)
                val = self._parse_convar_value(name, refresh)
                self.table.blockSignals(True)
                cur_item = self.table.item(target_row, 3)
                if cur_item is None:
                    cur_item = QTableWidgetItem("")
                    cur_item.setFlags(cur_item.flags() & ~Qt.ItemIsEditable)
                    self.table.setItem(target_row, 3, cur_item)
                cur_item.setText(val)
            finally:
                self.table.blockSignals(False)
            self.save_config()
        def _parse_convar_value(self, name: str, resp: str) -> str:
            lines = resp.splitlines()
            for ln in lines:
                if f"{name} =" in ln:
                    part = ln.split("=", 1)[1].strip()
                    if not part:
                        return ""
                    return part.split()[0].strip("\"'")
                if f"\"{name}\"" in ln and "\" = \"" in ln or "\" = " in ln:
                    i = ln.find("\" = ")
                    if i != -1:
                        part = ln[i + 4:].strip()
                        if part.startswith("\""):
                            j = part.find("\"", 1)
                            if j != -1:
                                return part[1:j]
                        if not part:
                            return ""
                        return part.split()[0].strip("\"'")
            return resp.strip().splitlines()[0] if resp.strip() else ""
        def on_import_convars(self):
            base = os.path.dirname(__file__)
            paths = [os.path.join(base, "convars.json"), os.path.join(base, "convars copy.json")]
            items = []
            any_found = False
            for p in paths:
                if os.path.exists(p):
                    any_found = True
                    try:
                        with open(p, "r", encoding="utf-8") as f:
                            obj = json.load(f)
                            if isinstance(obj, dict):
                                lst = obj.get("convars")
                                if isinstance(lst, list):
                                    items.extend([x for x in lst if isinstance(x, dict)])
                                else:
                                    for v in obj.values():
                                        if isinstance(v, list):
                                            items.extend([x for x in v if isinstance(x, dict)])
                            elif isinstance(obj, list):
                                items.extend([x for x in obj if isinstance(x, dict)])
                    except Exception as e:
                        self.output.appendPlainText(str(e))
                        return
            if not any_found:
                self.output.appendPlainText("未找到可导入的 ConVars 文件")
                return
            self.table.blockSignals(True)
            self.tree.blockSignals(True)
            try:
                for it in items:
                    name = it.get("name", "") or ""
                    zh = it.get("zh", "") or ""
                    grp, sub = self._categorize(name)
                    grp_item = self._ensure_group(grp)
                    if sub is None:
                        path_str = f"{grp}|"
                    else:
                        sub_item = self._ensure_child(grp_item, sub)
                        path_str = f"{grp}|{sub}"
                    if self._row_exists(name, path_str):
                        r = self._find_row(name, path_str)
                        if r is not None:
                            zh_item = self.table.item(r, 1) or QTableWidgetItem("")
                            zh_item.setText(zh or zh_item.text() or name)
                            self.table.setItem(r, 1, zh_item)
                        continue
                    r = self.table.rowCount()
                    self.table.insertRow(r)
                    name_item = QTableWidgetItem(name)
                    zh_item = QTableWidgetItem(zh or name)
                    init_item = QTableWidgetItem(it.get("initial", "") or "")
                    init_item.setFlags(init_item.flags() & ~Qt.ItemIsEditable)
                    cur_item = QTableWidgetItem("")
                    cur_item.setFlags(cur_item.flags() & ~Qt.ItemIsEditable)
                    desired_item = QTableWidgetItem("")
                    self.table.setItem(r, 0, name_item)
                    self.table.setItem(r, 1, zh_item)
                    self.table.setItem(r, 2, init_item)
                    self.table.setItem(r, 3, cur_item)
                    self.table.setItem(r, 4, desired_item)
                    self.table.item(r, 0).setData(Qt.UserRole, path_str)
                    btn = QPushButton("确认")
                    btn.clicked.connect(self.on_confirm_row)
                    self.table.setCellWidget(r, 5, btn)
                    get_btn = QPushButton("获取当前值")
                    get_btn.clicked.connect(self.on_fetch_row)
                    self.table.setCellWidget(r, 6, get_btn)
                self.apply_filters()
                self.save_config()
                self.output.appendPlainText("已导入 convars.json")
            finally:
                self.table.blockSignals(False)
                self.tree.blockSignals(False)
        def _row_exists(self, name: str, path: str) -> bool:
            return self._find_row(name, path) is not None
        def _find_row(self, name: str, path: str):
            for r in range(self.table.rowCount()):
                item = self.table.item(r, 0)
                if not item:
                    continue
                if item.text().strip() == name and (item.data(Qt.UserRole) or "") == path:
                    return r
            return None
        def _ensure_group(self, name: str) -> QTreeWidgetItem:
            for i in range(self.root_all.childCount()):
                child = self.root_all.child(i)
                if child.text(0) == name:
                    return child
            item = QTreeWidgetItem([name])
            item.setFlags(item.flags() | Qt.ItemIsEditable)
            item.setChildIndicatorPolicy(QTreeWidgetItem.DontShowIndicatorWhenChildless)
            self.root_all.addChild(item)
            return item
        def _ensure_child(self, group_item: QTreeWidgetItem, child_name: str) -> QTreeWidgetItem:
            for i in range(group_item.childCount()):
                c = group_item.child(i)
                if c.text(0) == child_name:
                    return c
            c = QTreeWidgetItem([child_name])
            c.setFlags(c.flags() | Qt.ItemIsEditable)
            group_item.addChild(c)
            return c
        def _categorize(self, name: str):
            weapon_prefixes = {"bizon","mac10","mp5","mp7","mp9","p90","ump45","m4a4","m4a4s","sg553","awp","scar20","g3sg1","ssg08"}
            for wp in weapon_prefixes:
                if name.lower().startswith(wp + "_"):
                    sub = wp[0].upper() + wp[1:]
                    return ("武器", sub)
            if name == "EntWatch_EPick":
                return ("插件设置", "EntWatch")
            if name.startswith("ze_infect_"):
                return ("感染设置", None)
            if name.startswith("ze_classes_"):
                return ("职业设置", None)
            if name.startswith("ze_respawn_"):
                return ("重生设置", None)
            if name == "ze_ztele_enable":
                return ("功能开关", None)
            if name.startswith("ze_award_"):
                suf = name[len("ze_award_"):]
                basics = {"human_base_exp","zombie_base_exp","human_base_point","zombie_base_point"}
                damage = {"exp_per_10k_damage","point_per_10k_damage"}
                infect = {"exp_per_infect","point_per_infect"}
                punish = {"human_defeat_exp","human_defeat_point"}
                people = {"people","mini_effect_player","mini_exp","mini_point"}
                coeffs = {"difficulty_multiplier","factor"}
                if suf in basics:
                    return ("奖励与积分", "基础奖励")
                if suf in damage:
                    return ("奖励与积分", "伤害奖励")
                if suf in infect:
                    return ("奖励与积分", "感染奖励")
                if suf in punish:
                    return ("奖励与积分", "失败惩罚")
                if suf in people:
                    return ("奖励与积分", "人数与暖服")
                if suf in coeffs:
                    return ("奖励与积分", "难度与系数")
                return ("奖励与积分", None)
            if name.startswith("ze_konckback_"):
                return ("击退", "整体设置")
            if name.startswith("Hit") and name.endswith("_Knockback"):
                return ("击退", "部位")
            if name.endswith("_Knockback"):
                prefix = name[:-len("_Knockback")]
                grenades = {"He","Fire","Flash","Frag","Smoke","Xz"}
                if prefix in grenades:
                    return ("击退", "投掷物")
                if prefix == "Vest":
                    return ("击退", "护甲")
                return ("武器", prefix)
            if name.startswith("zero_map"):
                if "votecout" in name:
                    return ("地图与投票", "地图投票")
                if "ext" in name or "exttime" in name:
                    return ("地图与投票", "地图延长")
                return ("地图与投票", None)
            if name == "mp_endmatch_votenextmap":
                return ("地图与投票", "地图投票")
            if name.startswith("sv_vote_") or name == "sv_allow_votes":
                return ("地图与投票", "投票设置")
            if name.startswith("mp_"):
                flows = {"mp_timelimit","mp_roundtime","mp_roundtime_defuse","mp_roundtime_hostage","mp_maxrounds","mp_winlimit","mp_round_restart_delay","mp_restartgame","mp_warmuptime","mp_warmup_pausetimer","mp_force_pick_time"}
                economy = {"mp_startmoney","mp_maxmoney","mp_afterroundmoney","mp_playercashawards","mp_teamcashawards","mp_free_armor"}
                buy = {"mp_buytime","mp_buy_anywhere"}
                defaults = {"mp_ct_default_primary","mp_t_default_primary","mp_ct_default_secondary","mp_t_default_secondary"}
                radar_spec = {"mp_radar_showall","mp_forcecamera","spec_freeze_time","spec_freeze_panel_extended"}
                friendly = {"mp_friendlyfire"}
                teams = {"mp_limitteams","mp_autoteambalance"}
                if name in flows:
                    return ("比赛流程", None)
                if name in economy:
                    return ("经济与购买", "经济")
                if name in buy:
                    return ("经济与购买", "购买")
                if name in defaults:
                    return ("经济与购买", "默认武器")
                if name in radar_spec:
                    return ("观战与雷达", None)
                if name in friendly:
                    return ("友伤与伤害", "友伤")
                if name in teams:
                    return ("队伍与平衡", None)
                return ("其他", None)
            if name.startswith("ff_damage_reduction_"):
                return ("友伤与伤害", "伤害比例")
            if name.startswith("tv_"):
                return ("SourceTV", None)
            if name.startswith("sv_"):
                if name in {"sv_lan","sv_pure","sv_hibernate_when_empty"}:
                    return ("服务器与网络", "服务器模式")
                if name in {"sv_voiceenable","sv_deadtalk","sv_alltalk"}:
                    return ("服务器与网络", "语音")
                if name == "sv_password":
                    return ("服务器与网络", "安全")
                if name.endswith("rate") or name.endswith("cmdrate") or name.endswith("updaterate"):
                    return ("服务器与网络", "网络速率")
                if name in {"sv_gravity","sv_accelerate","sv_airaccelerate","sv_stopspeed","sv_maxspeed"}:
                    return ("移动与物理", None)
                if name in {"sv_autobunnyhopping","sv_enablebunnyhopping"}:
                    return ("移动与物理", "连跳")
                return ("服务器与网络", None)
            if name.startswith("bot_"):
                return ("机器人设置", None)
            if name == "ammo_grenade_limit_total":
                return ("投掷物", None)
            return ("其他", None)
        def on_save_config(self):
            self.save_config()
            self.output.appendPlainText("已保存配置")
        def on_load_config(self):
            self.load_config()
            self.output.appendPlainText("已加载配置")
        def on_choose_config(self):
            start_dir = os.path.dirname(self.config_path) if isinstance(self.config_path, str) and self.config_path else os.getcwd()
            path, _ = QFileDialog.getOpenFileName(self, "选择配置 JSON", start_dir, "JSON 文件 (*.json);;所有文件 (*)")
            if path:
                self.config_path = path
                if hasattr(self, "config_path_display"):
                    self.config_path_display.setText(path)
                self.load_config()
                self.output.appendPlainText(f"已从文件加载配置: {path}")
        def save_config(self):
            data = {
                "connection": {
                    "host": self.host_edit.text().strip(),
                    "port": int(self.port_spin.value())
                },
                "convars": [],
                "groups": [],
                "ui": {
                    "window": {
                        "width": int(self.width()),
                        "height": int(self.height())
                    },
                    "columns": [int(self.table.columnWidth(i)) for i in range(self.table.columnCount())],
                    "splitter": [int(x) for x in self.splitter.sizes()]
                }
            }
            groups_map = {}
            for r in range(self.table.rowCount()):
                name = self.table.item(r, 0).text().strip() if self.table.item(r, 0) else ""
                zh = self.table.item(r, 1).text().strip() if self.table.item(r, 1) else ""
                initial = self.table.item(r, 2).text().strip() if self.table.item(r, 2) else ""
                path = self.table.item(r, 0).data(Qt.UserRole) if self.table.item(r, 0) else ""
                if name:
                    if isinstance(path, str) and path:
                        if "|" in path:
                            grp_name, weapon_name = path.split("|", 1)
                            if grp_name not in groups_map:
                                groups_map[grp_name] = {"convars": [], "weapons": {}}
                            item = {"name": name, "zh": zh}
                            if initial:
                                item["initial"] = initial
                            if weapon_name:
                                groups_map[grp_name]["weapons"].setdefault(weapon_name, []).append(item)
                            else:
                                groups_map[grp_name]["convars"].append(item)
                    else:
                        item = {"name": name, "zh": zh}
                        if initial:
                            item["initial"] = initial
                        data["convars"].append(item)
            for grp_name, payload in groups_map.items():
                grp_obj = {"name": grp_name}
                if payload.get("convars"):
                    grp_obj["convars"] = payload["convars"]
                weapons = payload.get("weapons", {})
                if weapons:
                    grp_obj["weapons"] = []
                    for weapon_name, convars in weapons.items():
                        grp_obj["weapons"].append({"name": weapon_name, "convars": convars})
                data["groups"].append(grp_obj)
            try:
                with open(self.config_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            except Exception as e:
                self.output.appendPlainText(str(e))
        def load_config(self):
            if not os.path.exists(self.config_path):
                return
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except Exception as e:
                self.output.appendPlainText(str(e))
                return
            conn = data.get("connection", {})
            host = conn.get("host")
            port = conn.get("port")
            if isinstance(host, str) and host:
                self.host_edit.setText(host)
            if isinstance(port, int) and 1 <= port <= 65535:
                self.port_spin.setValue(port)
            ui = data.get("ui", {})
            win = ui.get("window", {})
            w = win.get("width")
            h = win.get("height")
            if isinstance(w, int) and isinstance(h, int) and w > 0 and h > 0:
                self.resize(w, h)
                self._ui_applied = True
            sp = ui.get("splitter", [])
            if isinstance(sp, list) and len(sp) == 2 and all(isinstance(x, int) and x > 0 for x in sp):
                self.splitter.setSizes(sp)
            items = data.get("convars", [])
            self.table.blockSignals(True)
            self.table.setRowCount(0)
            for item in items:
                r = self.table.rowCount()
                self.table.insertRow(r)
                name_item = QTableWidgetItem(item.get("name", "") or "")
                zh_item = QTableWidgetItem(item.get("zh", "") or "")
                init_item = QTableWidgetItem(item.get("initial", "") or "")
                init_item.setFlags(init_item.flags() & ~Qt.ItemIsEditable)
                cur_item = QTableWidgetItem("")
                cur_item.setFlags(cur_item.flags() & ~Qt.ItemIsEditable)
                desired_item = QTableWidgetItem("")
                self.table.setItem(r, 0, name_item)
                self.table.setItem(r, 1, zh_item)
                self.table.setItem(r, 2, init_item)
                self.table.setItem(r, 3, cur_item)
                self.table.setItem(r, 4, desired_item)
                self.table.item(r, 0).setData(Qt.UserRole, "")
                btn = QPushButton("确认")
                btn.clicked.connect(self.on_confirm_row)
                self.table.setCellWidget(r, 5, btn)
                get_btn = QPushButton("获取当前值")
                get_btn.clicked.connect(self.on_fetch_row)
                self.table.setCellWidget(r, 6, get_btn)
            groups = data.get("groups", [])
            self.tree.blockSignals(True)
            for i in range(self.root_all.childCount() - 1, -1, -1):
                self.root_all.removeChild(self.root_all.child(i))
            for grp in groups:
                grp_item = QTreeWidgetItem([grp.get("name", "") or ""])
                grp_item.setFlags(grp_item.flags() | Qt.ItemIsEditable)
                grp_item.setChildIndicatorPolicy(QTreeWidgetItem.DontShowIndicatorWhenChildless)
                self.root_all.addChild(grp_item)
                for cv in grp.get("convars", []):
                    r = self.table.rowCount()
                    self.table.insertRow(r)
                    name_item = QTableWidgetItem(cv.get("name", "") or "")
                    zh_item = QTableWidgetItem(cv.get("zh", "") or "")
                    init_item = QTableWidgetItem(cv.get("initial", "") or "")
                    init_item.setFlags(init_item.flags() & ~Qt.ItemIsEditable)
                    cur_item = QTableWidgetItem("")
                    cur_item.setFlags(cur_item.flags() & ~Qt.ItemIsEditable)
                    desired_item = QTableWidgetItem("")
                    self.table.setItem(r, 0, name_item)
                    self.table.setItem(r, 1, zh_item)
                    self.table.setItem(r, 2, init_item)
                    self.table.setItem(r, 3, cur_item)
                    self.table.setItem(r, 4, desired_item)
                    self.table.item(r, 0).setData(Qt.UserRole, f"{grp_item.text(0)}|")
                    btn = QPushButton("确认")
                    btn.clicked.connect(self.on_confirm_row)
                    self.table.setCellWidget(r, 5, btn)
                    get_btn = QPushButton("获取当前值")
                    get_btn.clicked.connect(self.on_fetch_row)
                    self.table.setCellWidget(r, 6, get_btn)
                for weapon in grp.get("weapons", []):
                    weapon_item = QTreeWidgetItem([weapon.get("name", "") or ""])
                    weapon_item.setFlags(weapon_item.flags() | Qt.ItemIsEditable)
                    grp_item.addChild(weapon_item)
                    for cv in weapon.get("convars", []):
                        r = self.table.rowCount()
                        self.table.insertRow(r)
                        name_item = QTableWidgetItem(cv.get("name", "") or "")
                        zh_item = QTableWidgetItem(cv.get("zh", "") or "")
                        init_item = QTableWidgetItem(cv.get("initial", "") or "")
                        init_item.setFlags(init_item.flags() & ~Qt.ItemIsEditable)
                        cur_item = QTableWidgetItem("")
                        cur_item.setFlags(cur_item.flags() & ~Qt.ItemIsEditable)
                        desired_item = QTableWidgetItem("")
                        self.table.setItem(r, 0, name_item)
                        self.table.setItem(r, 1, zh_item)
                        self.table.setItem(r, 2, init_item)
                        self.table.setItem(r, 3, cur_item)
                        self.table.setItem(r, 4, desired_item)
                        self.table.item(r, 0).setData(Qt.UserRole, f"{grp_item.text(0)}|{weapon_item.text(0)}")
                        btn = QPushButton("确认")
                        btn.clicked.connect(self.on_confirm_row)
                        self.table.setCellWidget(r, 5, btn)
                        get_btn = QPushButton("获取当前值")
                        get_btn.clicked.connect(self.on_fetch_row)
                        self.table.setCellWidget(r, 6, get_btn)
            self.tree.blockSignals(False)
            cols = ui.get("columns", [])
            if isinstance(cols, list) and cols:
                for i in range(min(len(cols), self.table.columnCount())):
                    cw = cols[i]
                    if isinstance(cw, int) and cw > 0:
                        self.table.setColumnWidth(i, cw)
            self.table.blockSignals(False)
        def closeEvent(self, event):
            try:
                self.save_config()
                self.on_disconnect()
            finally:
                event.accept()
    app = QApplication([])
    w = RCONWindow()
    if not getattr(w, "_ui_applied", False):
        w.resize(1100, 800)
    w.show()
    app.exec_()
