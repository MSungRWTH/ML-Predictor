import os
import json
import pickle
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler, StandardScaler
import autokeras as ak
from concurrent.futures import ThreadPoolExecutor

# Directories
UPLOAD_DIRECTORY = "./datas/uploads/"  # same as data directory
MODEL_DIRECTORY = "./models/"
PROCESSED_DIRECTORY = "./datas/processed/"

def load_processed_data(file_prefix):
    """Load the processed training and testing data from .npz files."""
    try:
        # Use os.path.join to ensure proper path construction
        train_file_path = os.path.join(PROCESSED_DIRECTORY, f'{file_prefix}_train.npz')
        test_file_path = os.path.join(PROCESSED_DIRECTORY, f'{file_prefix}_test.npz')
        
        # Load the .npz files
        train_data = np.load(train_file_path)
        test_data = np.load(test_file_path)
        
        X_train, y_train = train_data['X'], train_data['y']
        X_test, y_test = test_data['X'], test_data['y']
        
        return X_train, X_test, y_train, y_test
    except Exception as e:
        print(f"Error loading processed data: {e}")
        raise


def train_model(tuner_type, X_train, y_train, X_val, y_val, project_name, scaler_X, scaler_y, input_params, output_params):
    """Train the model using the specified tuner and save the model and scalers."""
    regressor = ak.StructuredDataRegressor(
        project_name=project_name,
        tuner=tuner_type,
        max_trials=100,
        overwrite=True,
        loss='mean_absolute_error'
    )
    regressor.fit(X_train, y_train, validation_data=(X_val, y_val), epochs=100)
    
    # Save the model and scalers
    model_dir = os.path.join(MODEL_DIRECTORY, f"{project_name}_{tuner_type}")
    os.makedirs(model_dir, exist_ok=True)
    regressor.export_model().save(os.path.join(model_dir, "model.h5"))
    
    with open(os.path.join(model_dir, "scaler_X.pkl"), "wb") as f:
        pickle.dump(scaler_X, f)
    with open(os.path.join(model_dir, "scaler_y.pkl"), "wb") as f:
        pickle.dump(scaler_y, f)
    
    # Save input and output params
    params = {"input_params": input_params, "output_params": output_params}
    with open(os.path.join(model_dir, "params.json"), "w") as f:
        json.dump(params, f)
    
    print(f"Model saved at: {model_dir}")
    return model_dir


def preprocess_data(file_prefix, input_params, output_params, scaler_type):
    """Load and preprocess data using the specified scaler."""
    X_train, X_test, y_train, y_test = load_processed_data(file_prefix)

    # Apply the scaler to the data
    if scaler_type == 'StandardScaler':
        scaler_X = StandardScaler()
        scaler_y = StandardScaler()
    elif scaler_type == 'MinMaxScaler':
        scaler_X = MinMaxScaler()
        scaler_y = MinMaxScaler()

    X_train = scaler_X.fit_transform(X_train)
    y_train = scaler_y.fit_transform(y_train)
    X_test = scaler_X.transform(X_test)
    y_test = scaler_y.transform(y_test)

    return X_train, X_test, y_train, y_test, scaler_X, scaler_y


def main():
    # Define parameters
    project_name = "Experiment 1"  # Define a project name
    file_prefix = "data_1"  # Change this to match the processed file prefix
    input_params = ["AmountServer", "Coolingdefect", "InterarrivalTime", "defekteModulanzahl"]
    output_params = ["AverageServerUtilisation", "AverageFlowTime", "OEE", "TotalAverageQueueLength", 
                     "ProcessingTimeAverage", "WaitingTimeAverage", "MovingTimeAverage", "FailedTimeAverage", 
                     "BlockedTimeAverage", "Throughput"]
    scaler_type = "MinMaxScaler"  # or "StandardScaler"

    # Preprocess data
    X_train, X_test, y_train, y_test, scaler_X, scaler_y = preprocess_data(file_prefix, input_params, output_params, scaler_type)
    
    # Split data into validation set (X_val, y_val) using a portion of the training data
    X_train, X_val, y_train, y_val = train_test_split(X_train, y_train, test_size=0.1, random_state=42)
    
    # Train models with different tuners in parallel
    tuners = ['random', 'bayesian', 'hyperband', 'greedy']
    with ThreadPoolExecutor() as executor:
        futures = [executor.submit(train_model, tuner, X_train, y_train, X_val, y_val, project_name, 
                                  scaler_X, scaler_y, input_params, output_params) for tuner in tuners]
        for future in futures:
            future.result()  # Wait for the result and catch any exceptions


if __name__ == "__main__":
    main()
