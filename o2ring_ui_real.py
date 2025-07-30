import sys
import re
import asyncio
import threading
from PySide6.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, 
                               QWidget, QLabel, QHBoxLayout, QPushButton)
from PySide6.QtCore import Qt, QTimer, Signal, QThread
from PySide6.QtGui import QFont

# Import the o2r library
import o2r


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


class O2RingDataThread(QThread):
    """Thread to handle O2Ring data connection"""
    data_received = Signal(str)
    status_changed = Signal(str)
    
    def __init__(self):
        super().__init__()
        self.running = False
        self.manager = None
        
    def run(self):
        """Run the O2Ring data collection"""
        self.running = True
        self.status_changed.emit("Starting O2Ring discovery...")
        
        try:
            # Create event loop for asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Create O2Ring manager
            self.manager = o2r.O2DeviceManager()
            self.manager.verbose = 1
            self.manager.queue = asyncio.Queue()
            
            # Start discovery
            loop.run_until_complete(self.manager.start_discovery())
            self.status_changed.emit("Scanning for O2Ring devices...")
            
            # Process data
            while self.running:
                try:
                    # Get data from queue with timeout
                    cmd = loop.run_until_complete(asyncio.wait_for(self.manager.queue.get(), 1.0))
                    
                    if cmd:
                        (ident, command, data) = cmd
                        
                        if command == 'BTDATA':
                            # Process sensor data
                            if hasattr(data, 'cmd') and data.cmd == o2r.CMD_READ_SENSORS:
                                o2 = int(data.recv_data[0])
                                hr = int(data.recv_data[1])
                                batt = int(data.recv_data[7])
                                charging = int(data.recv_data[8])
                                motion = int(data.recv_data[9])
                                hr_strength = int(data.recv_data[10])
                                
                                # Format battery string
                                if charging > 0:
                                    if charging == 1:
                                        batts = f"{batt}%++"
                                    elif charging == 2:
                                        batts = "CHGD"
                                    else:
                                        batts = f"{batt:3d}%-{charging}"
                                else:
                                    batts = f"{batt:3d}%"
                                
                                # Create data line
                                data_line = f"[O2Ring {ident}] SpO2  {o2}%, HR  {hr} bpm, Perfusion Idx  {hr_strength}, motion   {motion}, batt  {batts}"
                                self.data_received.emit(data_line)
                                self.status_changed.emit("Connected - Receiving Data")
                        
                        elif command == 'READY':
                            self.status_changed.emit(f"Connected to {data['name']}")
                        
                        elif command == 'DISCONNECT':
                            self.status_changed.emit("Device disconnected")
                            
                except asyncio.TimeoutError:
                    continue
                except Exception as e:
                    self.status_changed.emit(f"Error: {str(e)}")
                    break
                    
        except Exception as e:
            self.status_changed.emit(f"Connection Error: {str(e)}")
        finally:
            if self.manager:
                loop.run_until_complete(self.manager.stop_discovery())
            loop.close()
    
    def stop(self):
        """Stop the data collection"""
        self.running = False
        if self.manager:
            asyncio.create_task(self.manager.stop_discovery())


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
        self.status_label = QLabel("Status: Waiting for connection...")
        status_font = QFont()
        status_font.setPointSize(18)
        self.status_label.setFont(status_font)
        self.status_label.setStyleSheet("color: #7f8c8d; padding: 10px; background-color: #f8f9fa; border-radius: 8px; margin-top: 20px;")
        layout.addWidget(self.status_label)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.connect_button = QPushButton("Connect to O2Ring")
        self.connect_button.setFont(QFont("Arial", 14))
        self.connect_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
        """)
        self.connect_button.clicked.connect(self.start_connection)
        button_layout.addWidget(self.connect_button)
        
        self.disconnect_button = QPushButton("Disconnect")
        self.disconnect_button.setFont(QFont("Arial", 14))
        self.disconnect_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
        """)
        self.disconnect_button.clicked.connect(self.stop_connection)
        self.disconnect_button.setEnabled(False)
        button_layout.addWidget(self.disconnect_button)
        
        layout.addLayout(button_layout)
        
        # Add stretch to push everything to the top
        layout.addStretch()
        
        # Initialize data thread
        self.data_thread = None
        
    def start_connection(self):
        """Start the O2Ring data connection"""
        if self.data_thread is None or not self.data_thread.isRunning():
            self.data_thread = O2RingDataThread()
            self.data_thread.data_received.connect(self.update_data)
            self.data_thread.status_changed.connect(self.update_status)
            self.data_thread.start()
            
            self.connect_button.setEnabled(False)
            self.disconnect_button.setEnabled(True)
    
    def stop_connection(self):
        """Stop the O2Ring data connection"""
        if self.data_thread and self.data_thread.isRunning():
            self.data_thread.stop()
            self.data_thread.wait()
            
            self.connect_button.setEnabled(True)
            self.disconnect_button.setEnabled(False)
            self.update_status("Disconnected")
    
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
            
        except Exception as e:
            self.update_status(f"Error parsing data: {str(e)}")
    
    def update_status(self, status: str):
        """Update the status label"""
        self.status_label.setText(f"Status: {status}")
        
        if "Connected" in status and "Error" not in status:
            self.status_label.setStyleSheet("color: #27ae60; padding: 10px; background-color: #f0f9f4; border-radius: 8px; margin-top: 20px;")
        elif "Error" in status:
            self.status_label.setStyleSheet("color: #e74c3c; padding: 10px; background-color: #fdf2f2; border-radius: 8px; margin-top: 20px;")
        else:
            self.status_label.setStyleSheet("color: #7f8c8d; padding: 10px; background-color: #f8f9fa; border-radius: 8px; margin-top: 20px;")
    
    def closeEvent(self, event):
        """Handle application close event"""
        if self.data_thread and self.data_thread.isRunning():
            self.data_thread.stop()
            self.data_thread.wait()
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