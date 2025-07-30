import sys
import re
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, 
                               QWidget, QLabel, QHBoxLayout)
from PySide6.QtCore import Qt, QTimer, pyqtSignal, QThread
from PySide6.QtGui import QFont


def parse_o2ring_data(line: str) -> dict:
    """
    Parse O2Ring data line and extract values.
    
    Expected format: [O2Ring 0098] SpO2  96%, HR  99 bpm, Perfusion Idx  34, motion   1, batt  100%
    
    Returns:
        dict: Dictionary containing extracted values with keys:
            - spo2: Oxygen saturation percentage
            - hr: Heart rate in bpm
            - perfusion_idx: Perfusion index
            - motion: Motion value
            - battery: Battery level percentage
    """
    # Initialize with default values
    result = {
        'spo2': '--',
        'hr': '--',
        'perfusion_idx': '--',
        'motion': '--',
        'battery': '--'
    }
    
    try:
        # Extract SpO2 value
        spo2_match = re.search(r'SpO2\s+(\d+)%', line)
        if spo2_match:
            result['spo2'] = spo2_match.group(1)
        
        # Extract HR value
        hr_match = re.search(r'HR\s+(\d+)\s+bpm', line)
        if hr_match:
            result['hr'] = hr_match.group(1)
        
        # Extract Perfusion Index
        perfusion_match = re.search(r'Perfusion Idx\s+(\d+)', line)
        if perfusion_match:
            result['perfusion_idx'] = perfusion_match.group(1)
        
        # Extract motion value
        motion_match = re.search(r'motion\s+(\d+)', line)
        if motion_match:
            result['motion'] = motion_match.group(1)
        
        # Extract battery level
        battery_match = re.search(r'batt\s+(\d+)%', line)
        if battery_match:
            result['battery'] = battery_match.group(1)
            
    except Exception as e:
        print(f"Error parsing O2Ring data: {e}")
    
    return result


class DataSimulator(QThread):
    """Simulate O2Ring data for testing purposes"""
    data_received = pyqtSignal(str)
    
    def run(self):
        import time
        import random
        
        # Simulate data every 2 seconds
        while True:
            spo2 = random.randint(95, 100)
            hr = random.randint(60, 100)
            perfusion_idx = random.randint(20, 50)
            motion = random.randint(0, 3)
            battery = random.randint(80, 100)
            
            data_line = f"[O2Ring 0098] SpO2  {spo2}%, HR  {hr} bpm, Perfusion Idx  {perfusion_idx}, motion   {motion}, batt  {battery}%"
            self.data_received.emit(data_line)
            time.sleep(2)


class O2RingWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("O2Ring Monitor")
        self.setGeometry(100, 100, 600, 500)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Create title label
        title_label = QLabel("O2Ring Monitor")
        title_font = QFont()
        title_font.setPointSize(28)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #2c3e50; margin-bottom: 20px;")
        layout.addWidget(title_label)
        
        # Create data labels with large font
        data_font = QFont()
        data_font.setPointSize(24)
        
        # SpO2 Label
        self.spo2_label = QLabel("SpO2: --")
        self.spo2_label.setFont(data_font)
        self.spo2_label.setStyleSheet("color: #e74c3c; padding: 10px; background-color: #fdf2f2; border-radius: 8px;")
        layout.addWidget(self.spo2_label)
        
        # HR Label
        self.hr_label = QLabel("HR: -- bpm")
        self.hr_label.setFont(data_font)
        self.hr_label.setStyleSheet("color: #e67e22; padding: 10px; background-color: #fef9f0; border-radius: 8px;")
        layout.addWidget(self.hr_label)
        
        # Perfusion Index Label
        self.perfusion_label = QLabel("Perfusion Index: --")
        self.perfusion_label.setFont(data_font)
        self.perfusion_label.setStyleSheet("color: #27ae60; padding: 10px; background-color: #f0f9f4; border-radius: 8px;")
        layout.addWidget(self.perfusion_label)
        
        # Motion Label
        self.motion_label = QLabel("Motion: --")
        self.motion_label.setFont(data_font)
        self.motion_label.setStyleSheet("color: #8e44ad; padding: 10px; background-color: #f8f4fd; border-radius: 8px;")
        layout.addWidget(self.motion_label)
        
        # Battery Label
        self.battery_label = QLabel("Battery: --%")
        self.battery_label.setFont(data_font)
        self.battery_label.setStyleSheet("color: #2980b9; padding: 10px; background-color: #f0f8ff; border-radius: 8px;")
        layout.addWidget(self.battery_label)
        
        # Status Label
        self.status_label = QLabel("Status: Waiting for data...")
        status_font = QFont()
        status_font.setPointSize(18)
        self.status_label.setFont(status_font)
        self.status_label.setStyleSheet("color: #7f8c8d; padding: 10px; background-color: #f8f9fa; border-radius: 8px; margin-top: 20px;")
        layout.addWidget(self.status_label)
        
        # Add stretch to push everything to the top
        layout.addStretch()
        
        # Initialize data simulator for testing
        self.simulator = DataSimulator()
        self.simulator.data_received.connect(self.update_data)
        self.simulator.start()
        
        # Update status
        self.status_label.setText("Status: Connected (Simulation Mode)")
        self.status_label.setStyleSheet("color: #27ae60; padding: 10px; background-color: #f0f9f4; border-radius: 8px; margin-top: 20px;")
    
    def update_data(self, data_line: str):
        """Update the UI with new O2Ring data"""
        try:
            # Parse the data
            data = parse_o2ring_data(data_line)
            
            # Update labels
            self.spo2_label.setText(f"SpO2: {data['spo2']}%")
            self.hr_label.setText(f"HR: {data['hr']} bpm")
            self.perfusion_label.setText(f"Perfusion Index: {data['perfusion_idx']}")
            self.motion_label.setText(f"Motion: {data['motion']}")
            self.battery_label.setText(f"Battery: {data['battery']}%")
            
            # Update status
            self.status_label.setText("Status: Connected - Receiving Data")
            self.status_label.setStyleSheet("color: #27ae60; padding: 10px; background-color: #f0f9f4; border-radius: 8px; margin-top: 20px;")
            
        except Exception as e:
            self.status_label.setText(f"Status: Error - {str(e)}")
            self.status_label.setStyleSheet("color: #e74c3c; padding: 10px; background-color: #fdf2f2; border-radius: 8px; margin-top: 20px;")
    
    def closeEvent(self, event):
        """Handle application close event"""
        if hasattr(self, 'simulator'):
            self.simulator.quit()
            self.simulator.wait()
        event.accept()


def main():
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show the main window
    window = O2RingWindow()
    window.show()
    
    # Run the application
    sys.exit(app.exec())


if __name__ == "__main__":
    main() 