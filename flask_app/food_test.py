import os
import busio
import board
import adafruit_tca9548a
import adafruit_vl53l0x
import time
import csv
import datetime as dt

class FoodSensorController:
    def __init__(self, cage_id, logger, directory="Food_sensor_values"):
        """
        Initializes the FoodSensorController with specified logger
          and directory.
        Parameters:
            logger (Logger): Logging instance for reporting sensor data.
            directory (str): The directory to store output data files.
        """
        self.cage_id = cage_id
        self.logger = logger
        self.directory = directory
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.tca = adafruit_tca9548a.TCA9548A(self.i2c)
        self.vl53 = adafruit_vl53l0x.VL53L0X(self.tca[0])
        self.run_flag = False
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)
        self.csv_file_path = os.path.join(self.directory, "Foodsensor_values")
        self.offset = 0
        self.current_hour = dt.datetime.now().hour
        self.update_file_path()

    def start_sensor(self):
        """
        Starts the food sensor and initiates continuous data recording.
        """
        self.run_flag = True
        self.run_sensor()

    def read_current_data(self):
        """
        Reads the current distance measurement from the VL53L0X sensor.

        Returns:
            int: The current distance measurement adjusted
            by calibration offset, or 0 if an error occurs.
        """
        try:
            distance = self.vl53.range
            return distance + self.offset if distance is not None else 0
        except Exception as e:
            print(f"Error reading sensor: {e}")
            return 0

    def run_sensor(self):
        """
        Continuously reads sensor data every second, writes it to a CSV file,
        and creates a new file each hour.
        """
        while self.run_flag:
            self.update_file_path()
            value = self.read_current_data()
            current_time = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.record_data(current_time, value)
            self.logger.report_data(value, "Food Sensor")
            print(f'Range: {value}mm')
            time.sleep(1.0)

    def calibrate_sensor(self, actual_distance):
        """
        Calibrates the sensor using a known actual distance to set
        the measurement offset.

        Parameters:
            actual_distance (int):
            The known actual distance to calibrate the sensor.
        """
        try:
            measured_distance = self.vl53.range
            if measured_distance is not None:
                self.offset = actual_distance - measured_distance
                print(f"Calibration complete. Offset set to {self.offset} mm.")
        except Exception as e:
            print(f"Error during calibration: {e}")

    def stop_sensor(self):
        """
        Stops the food sensor and ends the data recording loop.
        """
        self.run_flag = False

    def update_file_path(self):
        """
        Updates the file path for logging data based on the current time.
        Creates a new CSV file if it doesn't already exist.
        """
        now = dt.datetime.now()
        self.file_path = f'{self.directory}/Food_{now.strftime("%Y%m%d_%H")}.csv'
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(["Timestamp", "Distance (mm)"])

    def record_data(self, timestamp, value):
        """
        Records data to the current CSV file.

        Args:
            timestamp (str): The timestamp of the data reading.
            volts (float): The voltage reading to be recorded.
        """
        with open(self.file_path, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([timestamp, value])
