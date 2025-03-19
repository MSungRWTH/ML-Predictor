import json
import pickle
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

import autokeras as ak
import numpy as np
from keras.models import load_model
from sklearn.metrics import mean_absolute_error, r2_score

from app.config import MODEL_DIRECTORY, PROCESSED_DIRECTORY


class AutoMLRegressor:
    def __init__(
        self,
        train_data_path,
        scaler_x_path,
        scaler_y_path,
        tuner_types,
        project_name,
        no_trials,
        no_epochs,
    ):
        """
        Initialize the AutoMLRegressor with paths to training/testing data and scalers, and tuner types.

        Args:
            train_data_path (str): Path to the training data file.
            scaler_x_path (str): Path to the X scaler (for features).
            scaler_y_path (str): Path to the y scaler (for target).
            tuner_types (list): List of tuner types to be used in AutoML (e.g., 'random', 'hyperband', etc.).
            project_name (str): The name of the project to create directories for saving models and results.
            no_trials (str): The number of trials for training the models.
            no_epochs (str): The number of epochs taken to regressor fit the models.
        """
        self.train_data_path = train_data_path
        self.scaler_x_path = scaler_x_path
        self.scaler_y_path = scaler_y_path
        self.tuner_types = tuner_types if tuner_types else ["random", "hyperband", "greedy", "bayesian"]
        self.project_name = project_name
        self.no_trials = no_trials
        self.no_epochs = no_epochs
        self.models = {}

        # Define project directories under PROCESSED_DIRECTORY, MODEL_DIRECTORY
        self.project_dir = PROCESSED_DIRECTORY / project_name
        self.model_dir = MODEL_DIRECTORY

        # Ensure the directories exist
        if not self.project_dir.exists():
            self.project_dir.mkdir(parents=True)
        if not self.model_dir.exists():
            self.model_dir.mkdir(parents=True)

    def load_train_data(self):
        """
        Load the training data and the feature/target scalers.

        This method loads the training data from the provided path and deserializes
        the scalers for features (X) and target (y).
        """
        if self.train_data_path:
            train_data = np.load(self.train_data_path)
            self.X_train, self.y_train = train_data["X_train"], train_data["y_train"]
            with self.scaler_x_path.open("rb") as f:
                self.scaler_X = pickle.load(f)
            with self.scaler_y_path.open("rb") as f:
                self.scaler_y = pickle.load(f)

    def load_test_data(self, test_data_path):
        """
        Load the test data from the provided path.

        Args:
            test_data_path (str): Path to the test data file.
        """
        test_data = np.load(test_data_path)
        self.X_test, self.y_test = test_data["X_test"], test_data["y_test"]

    def train_automl_model(self, tuner_type):
        """
        Train an AutoML model using a specific tuner type.

        Args:
            tuner_type (str): The type of tuner to use (e.g., 'random', 'hyperband', etc.).
        """
        print(f"Training with tuner: {tuner_type}")

        regressor = ak.StructuredDataRegressor(
            project_name=f"{self.project_name}_{tuner_type}",  # Create a project folder based on tuner type
            directory=self.model_dir,  # Save the trained model under model directory
            tuner=tuner_type,
            max_trials=self.no_trials,  # User define the number of trials for AutoML
            overwrite=True,
            loss="mean_absolute_error",  # Loss function to minimize
        )

        start_time = time.time()

        # Fit the regressor model with training data
        regressor.fit(
            self.X_train, self.y_train, epochs=self.no_epochs, validation_split=0.1
        )  # User define the number of epochs for AutoML
        end_time = time.time()

        # Store the trained model and log the training time
        self.models[tuner_type] = regressor
        training_time = end_time - start_time

        # Save the training time to a JSON file
        training_time_path = self.model_dir / f"{self.project_name}_{tuner_type}" / "training_time.json"
        with training_time_path.open("w") as f:
            json.dump({"training_time": training_time}, f)


