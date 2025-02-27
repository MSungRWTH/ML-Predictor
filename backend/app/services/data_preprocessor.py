import ast
import os
import json
import logging
import pandas as pd
import numpy as np
import pickle
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.model_selection import train_test_split
from app.config import PROCESSED_DIRECTORY, UPLOAD_DIRECTORY

class DataPreprocessor:
    def __init__(self, project_name: str, scaler_type: str, input_params: list, output_params: list, file_name: str):
        # Set the project directory and file paths
        self.project_dir = os.path.join(PROCESSED_DIRECTORY, project_name)
        self.param_file = os.path.join(self.project_dir, "params.json")
        
        # Ensure the file exists
        if not os.path.exists(self.param_file):
            raise FileNotFoundError("Parameters file not found.")
        
        # Save the input/output parameters and scaler type
        self.input_params = input_params
        self.output_params = output_params
        self.scaler_type = scaler_type
        
        # Define the file path for the dataset
        self.file_path = os.path.join(UPLOAD_DIRECTORY, file_name)

        # Ensure the dataset file exists
        if not os.path.exists(self.file_path):
            raise FileNotFoundError("Dataset file not found.")

        # Load the dataset (CSV or JSON)
        self.data = pd.read_csv(self.file_path) if self.file_path.endswith(".csv") else pd.read_json(self.file_path)
        


    def extract_data(self):
        """
        Extract input and output data based on the specified parameters from the loaded JSON data.
        """
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
                    logging.warning("Missing input parameter '%s' for ID: %s", param, id_key)
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
                                logging.error("Invalid format for 'Throughput' at ID: %s", id_key)
                                break
                        else:
                            valid = False
                            logging.warning("Missing 'Throughput' parameter for ID: %s", id_key)
                            break
                    else:
                        value = self.data[param].get(id_key)
                        if value is not None:
                            temp_output_data[param] = value
                        else:
                            valid = False
                            logging.warning("Missing output parameter '%s' for ID: %s", param, id_key)
                            break

            if valid:
                for param in self.input_params:
                    input_data[param].append(temp_input_data[param])
                for param in self.output_params:
                    output_data[param].append(temp_output_data[param])

        logging.info("Extracted data with %d valid records.", len(input_data[self.input_params[0]]))
        return pd.DataFrame(input_data), pd.DataFrame(output_data)

    def clean_data(self, input_df, output_df):
        """
        Combine input and output data and clean it by removing any rows with missing values.
        """
        combined_data = pd.concat([input_df, output_df], axis=1)
        cleaned_data = combined_data.dropna()
        logging.info("Cleaned data shape: %s", cleaned_data.shape)
        return cleaned_data

    def scale_data(self, combined_data):
        """
        Scale the input and output data using the selected scaler (StandardScaler or MinMaxScaler).
        """
        if self.scaler_type == 'StandardScaler':
            scaler_X = StandardScaler()
            scaler_y = StandardScaler()
        elif self.scaler_type == 'MinMaxScaler':
            scaler_X = MinMaxScaler()
            scaler_y = MinMaxScaler()
        else:
            raise ValueError("Unsupported scaler type")

        logging.info("Scaling data using %s", self.scaler_type)

        X_scaled = scaler_X.fit_transform(combined_data[self.input_params])
        y_scaled = scaler_y.fit_transform(combined_data[self.output_params])

        return X_scaled, y_scaled, scaler_X, scaler_y

    def split_data(self, X_scaled, y_scaled):
        """
        Split the scaled data into 90% training and 10% testing data.
        """
        X_train, X_test, y_train, y_test = train_test_split(X_scaled, y_scaled, test_size=0.1, random_state=42)
        return X_train, X_test, y_train, y_test

    def save_data(self, X_train, X_test, y_train, y_test):
        """
        Save the training and testing data to .npz files.
        """
        np.savez(os.path.join(self.project_dir, "train_data.npz"), X_train=X_train, y_train=y_train)
        np.savez(os.path.join(self.project_dir, "test_data.npz"), X_test=X_test, y_test=y_test)
        logging.info("Training and testing data saved.")

    def save_scalers(self, scaler_X, scaler_y):
        """
        Save the scalers to pickle files for future use.
        """
        with open(os.path.join(self.project_dir, 'scaler_X.pkl'), 'wb') as f:
            pickle.dump(scaler_X, f)
        with open(os.path.join(self.project_dir, 'scaler_y.pkl'), 'wb') as f:
            pickle.dump(scaler_y, f)
        logging.info("Scalers saved.")

    def preprocess(self):
        input_df, output_df = self.extract_data()
        cleaned_data = self.clean_data(input_df, output_df)

        X_scaled, y_scaled, scaler_X, scaler_y = self.scale_data(cleaned_data)
        X_train, X_test, y_train, y_test = self.split_data(X_scaled, y_scaled)

        self.save_data(X_train, X_test, y_train, y_test)
        self.save_scalers(scaler_X, scaler_y)

        return {"message": "Preprocessing complete", "processed_data_preview": cleaned_data.head().to_dict()}

