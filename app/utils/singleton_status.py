# app/utils/singleton_status.py
from PyQt5.QtWidgets import QLabel


class StatusManager:
    _instance = None
    status_label = None

    @staticmethod
    def get_instance():
        if StatusManager._instance is None:
            StatusManager._instance = StatusManager()
        return StatusManager._instance

    def set_status_label(self, label: QLabel):
        self.status_label = label

    def get_status_label(self):
        return self.status_label
