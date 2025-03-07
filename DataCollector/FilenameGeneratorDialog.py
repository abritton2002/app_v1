from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QComboBox, QDateEdit, QMessageBox)
from PySide6.QtCore import QDate, Qt

class FilenameGeneratorDialog(QDialog):
    """
    Dialog for generating consistent filenames for EMG data collection sessions.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Dialog setup
        self.setWindowTitle("Generate Filename for EMG Data")
        self.setModal(True)
        
        # Main layout
        layout = QVBoxLayout()
        
        # Date input
        date_layout = QHBoxLayout()
        date_label = QLabel("Date:")
        self.date_input = QDateEdit()
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        date_layout.addWidget(date_label)
        date_layout.addWidget(self.date_input)
        layout.addLayout(date_layout)
        
        # TraqID input
        traqid_layout = QHBoxLayout()
        traqid_label = QLabel("TraqID:")
        self.traqid_input = QLineEdit()
        traqid_layout.addWidget(traqid_label)
        traqid_layout.addWidget(self.traqid_input)
        layout.addLayout(traqid_layout)
        
        # Athlete name input
        name_layout = QHBoxLayout()
        name_label = QLabel("Athlete Name:")
        self.name_input = QLineEdit()
        name_layout.addWidget(name_label)
        name_layout.addWidget(self.name_input)
        layout.addLayout(name_layout)
        
        # Session type selection
        type_layout = QHBoxLayout()
        type_label = QLabel("Session Type:")
        self.type_input = QComboBox()
        self.type_input.addItems([
            "mocap", 
            "longform", 
            "veloday", 
            "recovery", 
            "other"
        ])
        type_layout.addWidget(type_label)
        type_layout.addWidget(self.type_input)
        layout.addLayout(type_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        ok_button = QPushButton("Generate")
        ok_button.clicked.connect(self.accept)
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
        # Set layout
        self.setLayout(layout)
        
        # Result placeholder
        self.generated_filename = ""
    
    def validate_inputs(self):
        """
        Validate input fields before generating filename.
        
        Returns:
        --------
        list
            List of validation error messages, empty list if no errors
        """
        validation_errors = []
        
        # Validate TraqID
        traq_id = self.traqid_input.text().strip()
        if not traq_id:
            validation_errors.append("TraqID cannot be empty")
        elif not traq_id.isalnum():
            validation_errors.append("TraqID must be alphanumeric")
        
        # Validate Athlete Name
        name = self.name_input.text().strip()
        if not name:
            validation_errors.append("Athlete Name cannot be empty")
        elif not all(char.isalpha() or char.isspace() for char in name):
            validation_errors.append("Athlete Name must contain only letters and spaces")
        
        # If there are validation errors, show a message box
        if validation_errors:
            error_msg = "\n".join(validation_errors)
            QMessageBox.warning(self, "Validation Errors", error_msg)
        
        return validation_errors
    
    def accept(self):
        """
        Generate filename when OK is pressed.
        """
        # Validate inputs first
        validation_errors = self.validate_inputs()
        if validation_errors:
            return  # Stop if there are validation errors
        
        # Generate filename in MMDDYY_TraqID_FirstLast_sessiontype format
        date_str = self.date_input.date().toString("MMddyy")
        traq_id = self.traqid_input.text().strip()
        
        # Process name to get First and Last name
        name_parts = self.name_input.text().strip().split()
        if len(name_parts) == 1:
            name = name_parts[0]
        elif len(name_parts) >= 2:
            name = f"{name_parts[0]}{name_parts[-1]}"
        else:
            name = "Unknown"
        
        session_type = self.type_input.currentText()
        
        self.generated_filename = f"{date_str}_{traq_id}_{name}_{session_type}.csv"
        
        # Close dialog
        super().accept()
    
    def get_filename(self):
        """
        Return the generated filename.
        
        Returns:
        --------
        str
            Generated filename or empty string if canceled
        """
        return self.generated_filename