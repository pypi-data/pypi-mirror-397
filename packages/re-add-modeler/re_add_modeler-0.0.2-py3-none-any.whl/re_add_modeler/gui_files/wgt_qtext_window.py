from okin.base.chem_logger import chem_logger

from PySide6.QtWidgets import QApplication, QPushButton, QVBoxLayout, QDialog, QTextEdit, QHBoxLayout, QMessageBox

import os
import shutil
import json 

class AdvancedSettingsWidget(QDialog):
    def __init__(self,settings_file, custom_file, parent=None, title="Copasi"):
        self.logger = chem_logger.getChild(self.__class__.__name__)
        super().__init__(parent)
        self.setWindowTitle(title)
        layout = QVBoxLayout(self)
        self.text_edit = QTextEdit()
        layout.addWidget(self.text_edit)
        
        button_layout = QHBoxLayout()
        self.reset_button = QPushButton("Reset")
        self.reset_button.clicked.connect(self.reset_text)
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_text)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)

        button_layout.addWidget(self.reset_button, 1)
        button_layout.addWidget(self.cancel_button, 4.5)
        button_layout.addWidget(self.save_button, 4.5)
        layout.addLayout(button_layout)

        #* setupt initial file_content
        self.settings_file = settings_file
        self.custom_file_path = custom_file
        self.read_file()
        
    # def read_file(self):
    #     if not os.path.exists(self.custom_file_path):
    #         self.logger.info(f"Created new file: {self.custom_file_path} from {self.settings_file}")
    #         shutil.copyfile(self.settings_file, self.custom_file_path)
    #         with open(self.custom_file_path, 'r') as settings_f:
    #             settings_dict = json.load(settings_f)
    #             self.set_text(str(settings_dict))

    def read_file(self):
        if not os.path.exists(self.custom_file_path):
            self.logger.info(f"Created new file: {self.custom_file_path} from {self.settings_file}")
            shutil.copyfile(self.settings_file, self.custom_file_path)
        
        # Always load content into text_edit
        with open(self.custom_file_path, 'r') as settings_f:
            settings_dict = json.load(settings_f)
            self.set_text(json.dumps(settings_dict, indent=4))  # make it pretty

        with open(self.custom_file_path, 'w') as settings_f:
            json.dump(settings_dict, settings_f, indent=4)



    def set_text(self, text):
        json.loads(text)
        self.text_edit.setPlainText(text)
        
    # def save_text(self, text=None):
    #     if text:
    #         self.set_text(text)
    #     # Save the new content to the file
    #     new_content = text if text else self.text_edit.toPlainText()
    #     with open(self.custom_file_path, 'w') as file:
    #         # file.write(new_content)
    #         print(f"{self.custom_file_path = },\n{new_content = }")
    #         json.dump(new_content, file, indent=4)
    #         input("tenartn")
    #     self.set_text(new_content)

    def save_text(self, text=None):
        new_content = text if text else self.text_edit.toPlainText()
        try:
            parsed = json.loads(new_content)  # validate JSON
        except json.JSONDecodeError as e:
            QMessageBox.warning(self, "Invalid JSON", str(e))
            return

        with open(self.custom_file_path, 'w') as file:
            json.dump(parsed, file, indent=4)
        self.set_text(json.dumps(parsed, indent=4))


    def reset_text(self):
        reply = QMessageBox.question(self, 'Confirmation', 'Are you sure you want to reset the file?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            # Delete the file if "Yes" is selected
            try:
                os.remove(self.custom_file_path)
                self.read_file()
                # QMessageBox.information(self, "Reset", "File 'test.txt' deleted.")
            except FileNotFoundError:
                QMessageBox.information(self, "Reset", "File 'test.txt' does not exist.")

    def get_settings(self):
        with open(self.custom_file_path, 'r') as settings_f:
            # file_content = settings_f.read()
            settings_dict = json.load(settings_f)
        return settings_dict

    def get_gen_pop(self):
        settings = self.get_settings()
        nr_gen = settings["number_of_generations"]
        nr_pop = settings["population_size"]
        return nr_gen, nr_pop
        

if __name__ == "__main__":
    def show_advanced_copasi_dialog():
        filename = "test.txt"
        dialog = AdvancedSettingsWidget(settings_file=filename, custom_file="user_text.txt")
        
        dialog.exec()
    app = QApplication([])
    advanced_copasi_b = QPushButton("!")
    advanced_copasi_b.setFixedSize(100, 100)  # Adjust the size as needed
    advanced_copasi_b.clicked.connect(show_advanced_copasi_dialog)
    advanced_copasi_b.show()
    app.exec()
