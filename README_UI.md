# O2Ring Monitor UI

A PySide6 desktop application for displaying real-time O2Ring data in a beautiful, modern interface.

## Features

- **Real-time Data Display**: Shows SpO2, Heart Rate, Perfusion Index, Motion, and Battery level
- **Large, Readable Labels**: 24px font size for easy reading
- **Color-coded Values**: Each data type has its own color scheme
- **Status Monitoring**: Shows connection and data reception status
- **Modern UI**: Clean, professional design with rounded corners and proper spacing

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Running the Application

```bash
python o2ring_ui.py
```

### Current Implementation

The application currently runs in **simulation mode** for testing purposes. It generates random O2Ring data every 2 seconds to demonstrate the UI functionality.

### Integration with Real O2Ring Data

To connect with real O2Ring data, you can:

1. **Modify the DataSimulator class** to read from your actual O2Ring data source
2. **Replace the simulator** with a real data connection
3. **Use the existing o2r library** to connect to actual O2Ring devices

### Data Format

The application expects data in the following format:
```
[O2Ring 0098] SpO2  96%, HR  99 bpm, Perfusion Idx  34, motion   1, batt  100%
```

The `parse_o2ring_data()` function extracts:
- **SpO2**: Oxygen saturation percentage
- **HR**: Heart rate in beats per minute
- **Perfusion Index**: Signal quality indicator
- **Motion**: Motion detection value
- **Battery**: Battery level percentage

## UI Components

- **Main Window**: Titled "O2Ring Monitor"
- **Data Labels**: Large, color-coded labels for each measurement
- **Status Label**: Shows connection and data reception status
- **Responsive Layout**: Automatically adjusts to window size

## Customization

You can customize the UI by modifying:
- Colors in the `setStyleSheet()` calls
- Font sizes in the `QFont()` configurations
- Layout spacing and margins
- Window size and positioning

## Error Handling

The application includes error handling for:
- Data parsing errors
- Connection issues
- Invalid data formats

## Dependencies

- PySide6: Modern Qt framework for Python
- Standard Python libraries: sys, re, threading, time, random

## License

This project is part of the o2r library and follows the same license terms. 