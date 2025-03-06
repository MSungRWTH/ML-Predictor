import os
import time
import json
import autokeras as ak
from keras.models import load_model
import numpy as np
import pickle
from sklearn.metrics import mean_absolute_error, r2_score
from concurrent.futures import ProcessPoolExecutor, as_completed
from app.config import PROCESSED_DIRECTORY, MODEL_DIRECTORY

class AutoMLRegressor:
    def __init__(self, train_data_path=None, test_data_path=None, scaler_x_path=None, scaler_y_path=None,
                 tuner_types=None, project_name=None):
        """
        Initialize the AutoMLRegressor with paths to training/testing data and scalers, and tuner types.

        Args:
            train_data_path (str): Path to the training data file.
            test_data_path (str): Path to the test data file.
            scaler_x_path (str): Path to the X scaler (for features).
            scaler_y_path (str): Path to the y scaler (for target).
            tuner_types (list): List of tuner types to be used in AutoML (e.g., 'random', 'hyperband', etc.).
            project_name (str): The name of the project to create directories for saving models and results.
        """
        self.train_data_path = train_data_path
        self.test_data_path = test_data_path
        self.scaler_x_path = scaler_x_path
        self.scaler_y_path = scaler_y_path
        self.tuner_types = tuner_types if tuner_types else ['random', 'hyperband', 'greedy', 'bayesian']
        self.project_name = project_name
        self.models = {}

        # Define project directories under PROCESSED_DIRECTORY, MODEL_DIRECTORY
        self.project_dir = os.path.join(PROCESSED_DIRECTORY, project_name)
        self.model_dir = os.path.join(MODEL_DIRECTORY)

        # Ensure the directories exist
        os.makedirs(self.project_dir, exist_ok=True)
        os.makedirs(self.model_dir, exist_ok=True)

    def load_train_data(self):
        """
        Load the training data and the feature/target scalers.

        This method loads the training data from the provided path and deserializes
        the scalers for features (X) and target (y).
        """
        if self.train_data_path:
            train_data = np.load(self.train_data_path)
            self.X_train, self.y_train = train_data['X_train'], train_data['y_train']
            with open(self.scaler_x_path, 'rb') as f:
                self.scaler_X = pickle.load(f)
            with open(self.scaler_y_path, 'rb') as f:
                self.scaler_y = pickle.load(f)

    def load_test_data(self, test_data_path):
        """
        Load the test data from the provided path.

        Args:
            test_data_path (str): Path to the test data file.
        """
        test_data = np.load(test_data_path)
        self.X_test, self.y_test = test_data['X_test'], test_data['y_test']

    def train_model(self, tuner_type):
        """
        Train an AutoML model using a specific tuner type.

        Args:
            tuner_type (str): The type of tuner to use (e.g., 'random', 'hyperband', etc.).
        """
        print(f"Training with tuner: {tuner_type}")

        # Initialize the AutoKeras StructuredDataRegressor with the specified tuner
        regressor = ak.StructuredDataRegressor(
            project_name=f'{self.project_name}_{tuner_type}', # Create a project folder based on tuner type
            directory=self.model_dir, # Save the trained model under model directory
            tuner=tuner_type,
            max_trials=100,  # Maximum number of trials for AutoML
            overwrite=True,
            loss='mean_absolute_error'  # Loss function to minimize
        )

        start_time = time.time()

        # Fit the regressor model with training data
        regressor.fit(self.X_train, self.y_train, epochs=100, validation_split=0.1)  # Train with 100 epochs
        end_time = time.time()

        # Store the trained model and log the training time
        self.models[tuner_type] = regressor
        training_time = end_time - start_time

        # Save the training time to a JSON file
        training_time_path = os.path.join(self.model_dir, f'{self.project_name}_{tuner_type}', 'training_time.json')
        with open(training_time_path, 'w') as f:
            json.dump({'training_time': training_time}, f)

    def evaluate_model(self, tuner_type, X_test, y_test):
        """
        Evaluate a trained AutoML model using test data.

        Args:
            tuner_type (str): The type of tuner used to train the model.
            X_test (numpy array): Test features.
            y_test (numpy array): Test target values.

        Returns:
            tuple: Mean Absolute Error (MAE) and Mean Absolute Percentage Error (MAPE) for the model.
        """
        print(f"Loading best model for tuner: {tuner_type}")

        # Load the best model from the project folder
        best_model = load_model(os.path.join(self.model_dir, f'{self.project_name}_{tuner_type}','best_model'))
        predictions = best_model.predict(X_test)

        # Inverse transform the predictions and actual values to the original scale
        predictions_inverse = self.scaler_y.inverse_transform(predictions)
        y_test_inverse = self.scaler_y.inverse_transform(y_test)

        # Calculate evaluation metrics
        mae = mean_absolute_error(y_test_inverse, predictions_inverse)
        r2 = r2_score(y_test_inverse, predictions_inverse)

        # Calculate Mean Absolute Percentage Error (MAPE), avoiding division by zero
        non_zero_indices = y_test_inverse != 0
        if np.any(non_zero_indices):
            mape = np.mean(np.abs(
                (y_test_inverse[non_zero_indices] - predictions_inverse[non_zero_indices]) / y_test_inverse[
                    non_zero_indices])) * 100
        else:
            mape = float('nan')

        print(f"Overall MAE for tuner {tuner_type}: {mae}")
        print(f"Overall R² for tuner {tuner_type}: {r2}")
        print(f"Overall MAPE for tuner {tuner_type}: {mape}%")
        return mae, mape

    def run_train_only(self):
        """
        Run the training process for each tuner type in parallel.

        This method uses concurrent futures to parallelize the training of different models.
        """
        with ProcessPoolExecutor() as executor:
            # Submit training tasks for each tuner type to the executor
            futures = {executor.submit(self.train_model, tuner_type): tuner_type for tuner_type in self.tuner_types}

            for future in as_completed(futures):
                tuner_type = futures[future]
                try:
                    future.result()
                    print(f"{tuner_type} training completed successfully.")
                except Exception as exc:
                    print(f"{tuner_type} generated an exception: {exc}")

        print("All training tasks completed.")
