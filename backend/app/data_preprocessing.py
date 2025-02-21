import json
import ast
import pandas as pd
import numpy as np
import pickle
import logging
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.model_selection import train_test_split

# Logging setup
logging.basicConfig(filename='data_preprocessing.log', level=logging.INFO)

class DataPreprocessor:
    def __init__(self, file_path, input_params, output_params, scaler_type='MinMaxScaler', test_size=0.2):
        self.file_path = file_path
        self.input_params = input_params
        self.output_params = output_params
        self.scaler_type = scaler_type
        self.test_size = test_size
        self.data = self.load_json()

    def load_json(self):
        """Load data from JSON file."""
        try:
            with open(self.file_path, 'r') as file:
                data = json.load(file)
                logging.info(f"Successfully loaded JSON data from {self.file_path}")
                return data
        except Exception as e:
            logging.error(f"Failed to load JSON file: {str(e)}")
            raise

    def extract_data(self):
        """Extract input and output data based on specified parameters."""
        input_data = {param: [] for param in self.input_params}
        output_data = {param: [] for param in self.output_params}
        ids = self.data[self.input_params[0]].keys()

        for id_key in ids:
            valid = True
            temp_input_data = {}
            temp_output_data = {}

            for param in self.input_params:
                value = self.data[param].get(id_key)
                if value is not None:
                    temp_input_data[param] = value
                else:
                    valid = False
                    logging.warning(f"Missing input parameter '{param}' for ID: {id_key}")
                    break

            if valid:
                for param in self.output_params:
                    if param == 'Throughput':
                        throughput_value = self.data[param].get(id_key)
                        if throughput_value is not None:
                            try:
                                temp_output_data[param] = ast.literal_eval(throughput_value)['Sink']
                            except (ValueError, SyntaxError):
                                valid = False
                                logging.error(f"Invalid format for 'Throughput' at ID: {id_key}")
                                break
                        else:
                            valid = False
                            logging.warning(f"Missing 'Throughput' parameter for ID: {id_key}")
                            break
                    else:
                        value = self.data[param].get(id_key)
                        if value is not None:
                            temp_output_data[param] = value
                        else:
                            valid = False
                            logging.warning(f"Missing output parameter '{param}' for ID: {id_key}")
                            break

            if valid:
                for param in self.input_params:
                    input_data[param].append(temp_input_data[param])
                for param in self.output_params:
                    output_data[param].append(temp_output_data[param])

        logging.info(f"Extracted data with {len(input_data[self.input_params[0]])} valid records.")
        return pd.DataFrame(input_data), pd.DataFrame(output_data)

    def clean_data(self, input_df, output_df):
        """Combine input and output data and clean it by removing rows with missing values."""
        combined_data = pd.concat([input_df, output_df], axis=1)
        cleaned_data = combined_data.dropna()
        logging.info(f"Cleaned data shape: {cleaned_data.shape}")
        return cleaned_data

    def process_data(self, combined_data):
        """Scale the input and output data using specified scaler."""
        if self.scaler_type == 'StandardScaler':
            scaler_X = StandardScaler()
            scaler_y = StandardScaler()
        elif self.scaler_type == 'MinMaxScaler':
            scaler_X = MinMaxScaler()
            scaler_y = MinMaxScaler()

        X_processed = scaler_X.fit_transform(combined_data[self.input_params])
        y_processed = scaler_y.fit_transform(combined_data[self.output_params])
        logging.info(f"Data scaling completed using {self.scaler_type}")
        return X_processed, y_processed, scaler_X, scaler_y

    def save_data(self, X_processed, y_processed, usage, index):
        """Save processed data to .npz files for training/testing."""
        file_prefix = f"{usage}_data_{index}"
        np.savez(f'{file_prefix}.npz', X=X_processed, y=y_processed)
        logging.info(f"Saved {usage} data to {file_prefix}.npz")

    def save_scalers(self, scaler_X, scaler_y):
        """Save scalers to pickle files."""
        with open('scaler_X.pkl', 'wb') as f:
            pickle.dump(scaler_X, f)
        with open('scaler_y.pkl', 'wb') as f:
            pickle.dump(scaler_y, f)
        logging.info("Scalers saved to scaler_X.pkl and scaler_y.pkl")

    def run(self, usage, index):
        """Main preprocessing pipeline: extraction, cleaning, processing, and saving."""
        try:
            # Step 1: Extract data
            input_df, output_df = self.extract_data()

            # Step 2: Clean the data
            cleaned_data = self.clean_data(input_df, output_df)

            # Step 3: Process the data (scaling)
            X_processed, y_processed, scaler_X, scaler_y = self.process_data(cleaned_data)

            # Step 4: Split data into training and testing
            X_train, X_test, y_train, y_test = train_test_split(X_processed, y_processed, test_size=self.test_size, random_state=42)
            logging.info(f"Data split into train (X_train: {X_train.shape}, y_train: {y_train.shape}) and test (X_test: {X_test.shape}, y_test: {y_test.shape})")

            # Step 5: Save processed data
            self.save_data(X_train, y_train, usage='train', index=index)
            self.save_data(X_test, y_test, usage='test', index=index)

            # Step 6: Save scalers
            self.save_scalers(scaler_X, scaler_y)

        except Exception as e:
            logging.error(f"Data Preprocessing Failed: {str(e)}")
            raise

# Standalone execution for testing
if __name__ == '__main__':
    # Specify input/output parameters and scaler type
    input_params = ['AmountServer', 'Coolingdefect', 'InterarrivalTime', 'defekteModulanzahl']
    output_params = ['OEE', 'TotalAverageQueueLength', 'ProcessingTimeAverage', 'WaitingTimeAverage', 'MovingTimeAverage', 'FailedTimeAverage', 'BlockedTimeAverage', 'Throughput']
    scaler_type = 'MinMaxScaler'  # or 'StandardScaler'

    # Provide file path to JSON data (adjust accordingly)
    file_path = './datas/uploads/scenario_analysis_result_MAN_Test_hl.json'

    # Instantiate the data processor and run the preprocessing
    preprocessor = DataPreprocessor(file_path, input_params, output_params, scaler_type)
    preprocessor.run(usage='train', index=1)