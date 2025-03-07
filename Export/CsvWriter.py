import csv
import os
from datetime import datetime

class CsvWriter:
    def __init__(self):
        # Lists to store header information
        self.h1_sensors = []
        self.h2_channels = []
        
        # Data storage
        self.data = []
        
        # Output file path (adjust this when the time comes)
        self.output_directory = r"C:\Users\alex.britton\Documents\DelsysTesting\Pitching_DataSet"
        os.makedirs(self.output_directory, exist_ok=True)
        
        # Custom filename (optional)
        self.custom_filename = None
    
    def set_custom_filename(self, filename):
        """
        Set a custom filename for export.
        
        Parameters:
        -----------
        filename : str
            Custom filename to use for export
        """
        self.custom_filename = filename
    
    def appendSensorHeader(self, selectedSensor):
        """
        Append sensor header information.
        
        Parameters:
        -----------
        selectedSensor : Delsys Sensor Object
            Sensor object to extract header information from
        """
        # Add sensor name or identifier to the headers
        sensor_name = f"({selectedSensor.PairNumber}) {selectedSensor.FriendlyName}"
        self.h1_sensors.append(sensor_name)
    
    def appendChannelHeader(self, channel_object):
        """
        Append channel header information.
        
        Parameters:
        -----------
        channel_object : Delsys Channel Object
            Channel object to extract header information from
        """
        # Construct channel header with name and sample rate
        channel_header = f"{channel_object.Name} ({channel_object.SampleRate} Hz)"
        self.h2_channels.append(channel_header)
    
    def appendYTChannelHeader(self, channel_object):
        """
        Append YT (Time-Y) channel header information.
        
        Parameters:
        -----------
        channel_object : Delsys Channel Object
            Channel object to extract header information from
        """
        # Similar to appendChannelHeader, but could be customized for YT data
        channel_header = f"{channel_object.Name} (YT) ({channel_object.SampleRate} Hz)"
        self.h2_channels.append(channel_header)
    
    def appendSensorHeaderSeperator(self):
        """
        Add a separator between sensor headers.
        """
        self.h1_sensors.append(",")
    
    def appendYTSensorHeaderSeperator(self):
        """
        Add a separator for YT sensor headers.
        """
        self.h1_sensors.append(",")
    
    def cleardata(self):
        """
        Clear stored data.
        """
        self.data = []
        self.h1_sensors = []
        self.h2_channels = []
        self.custom_filename = None
    
    def clearall(self):
        """
        Completely reset the writer.
        """
        self.cleardata()
    
    def exportCSV(self):
        """
        Export collected data to a CSV file in the exact Trigno Discover format.
        
        Returns:
        --------
        str
            Path to the exported CSV file
        """
        # Use custom filename if provided, otherwise generate a default
        if self.custom_filename:
            filename = os.path.join(self.output_directory, self.custom_filename)
        else:
            # Fallback to timestamp-based filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(self.output_directory, f"delsys_data_{timestamp}.csv")
        
        try:
            # Current date and time
            date_now = datetime.now().strftime('%m/%d/%Y %I:%M:%S %p')
            
            # Get sensor IDs and names - these should be set by the GUI
            muscle1_id = getattr(self, 'muscle1_id', "81728")  # Default ID
            muscle2_id = getattr(self, 'muscle2_id', "81745")  # Default ID
            
            # Extract muscle names from class attributes or use defaults
            muscle1_name = getattr(self, 'muscle1_name', "")  # No default
            muscle2_name = getattr(self, 'muscle2_name', "")  # No default
            
            # Use generic names for display if no custom names were set
            muscle1_display = muscle1_name if muscle1_name else "Muscle 1"
            muscle2_display = muscle2_name if muscle2_name else "Muscle 2"
            
            # Extract sampling rates from channel headers (or use defaults)
            sampling_rate1 = 1259.2593  # Default for first muscle
            sampling_rate2 = 2148.1481  # Default for second muscle
            
            if len(self.h2_channels) >= 2:
                for i, channel in enumerate(self.h2_channels):
                    if i == 0 and "Hz" in channel:
                        hz_index = channel.find('Hz')
                        paren_start = channel.find('(')
                        if paren_start != -1 and hz_index != -1:
                            try:
                                rate_text = channel[paren_start+1:hz_index].strip()
                                # Handle commas in sampling rate
                                rate_text = rate_text.replace(',', '')
                                sampling_rate1 = float(rate_text)
                            except ValueError:
                                pass
                    elif i == 1 and "Hz" in channel:
                        hz_index = channel.find('Hz')
                        paren_start = channel.find('(')
                        if paren_start != -1 and hz_index != -1:
                            try:
                                rate_text = channel[paren_start+1:hz_index].strip()
                                # Handle commas in sampling rate
                                rate_text = rate_text.replace(',', '')
                                sampling_rate2 = float(rate_text)
                            except ValueError:
                                pass
            
            # Calculate collection length (use actual data or default)
            collection_length = 1180.3455  # Default
            if len(self.data) >= 2 and len(self.data[0]) > 0:
                try:
                    # If we have time data
                    if len(self.data) >= 4:
                        last_time = max(self.data[0][-1], self.data[2][-1])
                        collection_length = round(last_time, 4)
                    # If we only have EMG data
                    else:
                        max_samples = max(len(self.data[0]), len(self.data[1]))
                        # Estimate time based on sample rate
                        collection_length = round(max_samples / max(sampling_rate1, sampling_rate2), 4)
                except Exception as e:
                    print(f"Error calculating collection length: {e}")
            
            with open(filename, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write exact Trigno Discover headers
                writer.writerow(["Application:", "Trigno Discover (1.7.0)"])
                writer.writerow(["Date/Time:", date_now])
                writer.writerow(["Collection Length (seconds):", str(collection_length)])
                writer.writerow([f"{muscle1_display} ({muscle1_id})", "", f"{muscle2_display} ({muscle2_id})"])
                writer.writerow(["sensor mode: 50", "", "sensor mode: 40"])
                writer.writerow(["EMG 1 Time Series (s)", "EMG 1 (mV)", "EMG 1 Time Series (s)", "EMG 1 (mV)"])
                writer.writerow(["", f"{sampling_rate1} Hz", "", f"{sampling_rate2} Hz"])
                
                # Process data
                if len(self.data) < 2:
                    print("Warning: Not enough data channels (need at least 2)")
                    return ""
                
                # Handle different data scenarios
                if len(self.data) == 2:
                    # We have only EMG channels, need to generate time series
                    emg1 = self.data[0]
                    emg2 = self.data[1]
                    
                    # Generate time series using sampling rates
                    time_step1 = 1.0 / sampling_rate1
                    time_step2 = 1.0 / sampling_rate2
                    
                    time1 = [round(i * time_step1, 7) for i in range(len(emg1))]
                    time2 = [round(i * time_step2, 7) for i in range(len(emg2))]
                    
                    # Determine number of samples to write
                    min_length = min(len(emg1), len(emg2))
                    
                    # Write data rows
                    for i in range(min_length):
                        writer.writerow([time1[i], emg1[i], time2[i], emg2[i]])
                    
                elif len(self.data) >= 4:
                    # Assume format is Time1, EMG1, Time2, EMG2
                    time1 = self.data[0]
                    emg1 = self.data[1]
                    time2 = self.data[2]
                    emg2 = self.data[3]
                    
                    # Determine number of samples to write
                    min_length = min(len(time1), len(emg1), len(time2), len(emg2))
                    
                    # Write data rows
                    for i in range(min_length):
                        writer.writerow([time1[i], emg1[i], time2[i], emg2[i]])
                
            print(f"CSV exported to {filename} in Trigno Discover format")
            return filename
        
        except Exception as e:
            print(f"Error exporting CSV: {e}")
            import traceback
            traceback.print_exc()
            return ""


    def set_muscle_names(self, muscle1_name="", muscle2_name="", muscle1_id="81728", muscle2_id="81745"):
        """
        Set custom muscle names and IDs for export.
        
        Parameters:
        -----------
        muscle1_name : str
            Name for the first muscle (default: empty string)
        muscle2_name : str
            Name for the second muscle (default: empty string)
        muscle1_id : str
            ID for the first muscle (default: "81728")
        muscle2_id : str
            ID for the second muscle (default: "81745")
        """
        self.muscle1_name = muscle1_name
        self.muscle2_name = muscle2_name
        self.muscle1_id = muscle1_id
        self.muscle2_id = muscle2_id
        print(f"Muscle names set: {muscle1_name} ({muscle1_id}), {muscle2_name} ({muscle2_id})")
    
    def exportYTCSV(self):
        """
        Export YT (Time-Y) data to a CSV file.
        
        Returns:
        --------
        str
            Path to the exported CSV file
        """
        # Similar to exportCSV, but could be customized for YT data format
        if self.custom_filename:
            filename = os.path.join(self.output_directory, self.custom_filename)
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(self.output_directory, f"delsys_yt_data_{timestamp}.csv")
        
        try:
            with open(filename, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write headers
                writer.writerow(self.h1_sensors)
                writer.writerow(self.h2_channels)
                
                # YT data might require special handling depending on data structure
                # This is a generic implementation
                max_length = max(len(channel) for channel in self.data)
                padded_data = [
                    channel + [None] * (max_length - len(channel)) 
                    for channel in self.data
                ]
                
                transposed_data = list(map(list, zip(*padded_data)))
                writer.writerows(transposed_data)
            
            print(f"YT CSV exported to {filename}")
            return filename
        
        except Exception as e:
            print(f"Error exporting YT CSV: {e}")
            return ""