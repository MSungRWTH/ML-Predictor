import pandas as pd
import json
import random 
import os 



# Method 1: Merging two json
# scenario_analysis_result_MAN_Test_hl.json
# scenario_analysis_result_MAN_Test_hl_new.json

# def merge_json_files(file1, file2, output_file):
#     # Load both JSON files
#     df1 = pd.read_json('scenario_analysis_result_MAN_Test_hl_new.json')  # First file (ID_0 to ID_959)
#     df2 = pd.read_json('scenario_analysis_result_MAN_Test_hl.json')  # Second file (ID_0 to ID_3839)

#     # Reset index for both to avoid duplicate indices
#     df1 = df1.reset_index(drop=True)
#     df2 = df2.reset_index(drop=True)

#     # Concatenate both DataFrames
#     combined_df = pd.concat([df1, df2], ignore_index=True)

#     # Assign new unique ID from 0 to 4559
#     combined_df.insert(0, "ID", [f"ID_{i}" for i in range(len(combined_df))])

#     # Save to a new JSON file
#     combined_df.to_json(output_file, orient="records", indent=4)

#     print(f"Merged file saved as {output_file} with new unique IDs from ID_0 to ID_4559")

# if __name__ == "__main__":
#     merge_json_files("scenario_analysis_result_MAN_Test_hl_new.json", "scenario_analysis_result_MAN_Test_hl.json", "combined4800.json")
    


# Method 2: Adding a new entry called EnergyConsumed [kWh]
# def modify_json_file(file_path):
#     try:
#         # Load JSON data from the file
#         with open(file_path, "r") as file:
#             data = json.load(file)

#         # Ensure the JSON data is a list of dictionaries (or it can be another structure)
#         if isinstance(data, list):
#             for entry in data:
#                 if isinstance(entry, dict):
#                     # Check if the entry has an "ID" key
#                     if "ID" in entry:
#                         # Add the "EnergyConsumed [kWh]" field with a random value between 80 - 100
#                         entry["EnergyConsumed [kWh]"] = round(random.uniform(80, 100), 2)

#             # Save the modified JSON back to the file
#             with open(file_path, "w") as file:
#                 json.dump(data, file, indent=4)

#             print(f"✅ Successfully updated {file_path}")

#         else:
#             print("⚠️ JSON structure is not a list of dictionaries. No changes made.")

#     except FileNotFoundError:
#         print("❌ Error: File not found.")
#     except json.JSONDecodeError:
#         print("❌ Error: Invalid JSON format.")

# if __name__ == "__main__":
#     # Ensure you pass the correct file path here
#     file_path = input("Enter the path to the JSON file (e.g., combined4800.json): ")
#     modify_json_file(file_path)



# Method 3: Calculating a new entry call CFP [kgC02/kWh]
def process_data(input_file, output_file):
    # Load the existing data from the JSON file
    with open(input_file, 'r') as f:
        data = json.load(f)
    
    # Check if the data is a list (not a dictionary)
    if isinstance(data, list):
        # Iterate over each item in the list
        for item in data:
            # Check if 'EnergyConsumed [kWh]' exists and calculate 'CFP [kgC02/kWh]'
            if 'EnergyConsumed [kWh]' in item:
                energy_consumed = item['EnergyConsumed [kWh]']
                cfp_value = energy_consumed * 0.321
                item['CFP [kgC02/kWh]'] = cfp_value  # Add new value with the correct key
    else:
        print("Error: The data is not in the expected format (list).")
        return

    # Save the updated data with the new values into a new JSON file
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=4)
    print(f"Updated data saved to {output_file}")

# Main function
def main():
    input_file = 'combined4800.json'  # Replace with your input file path
    output_file = 'modified4800.json'  # Replace with your desired output file path
    process_data(input_file, output_file)

if __name__ == "__main__":
    main()