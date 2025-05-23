import os
import glob
import json
import numpy as np
import re
import pandas as pd
from dtw import *
import argparse
# from json_server import JsonSender

def jsontoarray(data, part):
    data = json.loads(data)
    # print(f"Processing part: {part}")
    # print(f"wristFlexionData: {data['wristFlexionData']}")
    data_part = np.array(data[part])
    if part[-12:] == 'LocationData':
        array_data = np.zeros((data_part.shape[0], 3))
        columnnum = 0
        rownum = 0
        for row in data_part:
            for column in row:
                if np.isnan(row[column]):
                    array_data[rownum, columnnum] = 0
                else:
                    array_data[rownum, columnnum] = row[column]
                columnnum += 1
            columnnum = 0
            rownum += 1
    elif part[-8:] == 'QuatData':
        array_data = np.zeros((data_part.shape[0], 4))
        columnnum = 0
        rownum = 0
        for row in data_part:
            for column in row:
                if np.isnan(row[column]):
                    array_data[rownum, columnnum] = 0
                else:
                    array_data[rownum, columnnum] = row[column]
                columnnum += 1
            columnnum = 0
            rownum += 1
    else:
        array_data = np.zeros((data_part.shape[0], 1))
        columnnum = 0
        rownum = 0
        for row in data_part:
            array_data[rownum, columnnum] = row
            rownum += 1

    return array_data

def smart_inverter(array):
    negation = -array
    return negation + 1.72 * array[0]

def extract_number(filename):
    # Extract the number right before the '.json' extension
    match = re.search(r'_(\d+)\.json$', filename)
    return int(match.group(1)) if match else float('inf')

def sort_key(filename):
    # Extract base name
    base_name = os.path.basename(filename)
    
    # Determine if the file is "stroke" or "healthy"
    if "stroke" in base_name:
        prefix_priority = 1
    elif "healthy" in base_name:
        prefix_priority = 2
    else:
        prefix_priority = 3  # Just in case other types of files are present
    
    # Get the number from the filename
    number = extract_number(base_name)
    
    # For healthy files, we want to sort by number in ascending order, so no need to negate
    return (prefix_priority, number)

def load_json_files_from_folder(folder_path):
    parts = [ 
        "thumbDistalLocationData", 
        "thumbProximalLocationData", 
        "thumbMetacarpalLocationData", 
        "indexDistalLocationData", 
        "indexProximalLocationData", 
        "indexMetacarpalLocationData", 
        "middleDistalLocationData", 
        "middleProximalLocationData", 
        "middleMetacarpalLocationData", 
        "ringDistalLocationData", 
        "ringProximalLocationData", 
        "ringMetacarpalLocationData", 
        "littleDistalLocationData", 
        "littleProximalLocationData", 
        "littleMetacarpalLocationData", 
        "headLocationData", 
        "wristLocationData", 
        "armLowerLocationData", 
        "armUpperLocationData"
    ]
    
    json_files = glob.glob(os.path.join(folder_path, '*.json'))
    json_files.sort(key=sort_key)

    print(f'dtw_location.py: json_files: {json_files}')

    data_arrays = {part: [] for part in parts}
    for json_file in json_files:
        print(f'dtw_location.py: json_file: {json_file}')
        with open(json_file, 'r') as file:
            data = json.load(file)
            for part in parts:
                data_arrays[part].append(jsontoarray(data, part))
    return data_arrays

def calc_perc_df(folder_path, thresholds, thresholds_new):
    data_arrays = load_json_files_from_folder(folder_path)
    # print(f"data_arrays{data_arrays}")
    results = []
    for key in data_arrays.keys():
        for i in range(len(data_arrays[key]) - 1):
            reference = data_arrays[key][-1]
            query = data_arrays[key][i]
            inverted_reference = smart_inverter(reference)
            alignment = dtw(query, reference)
            wq = warp(alignment, index_reference = False)
            query_dist_capped = 0
            for x in range(len(reference)):
                capped_distance = np.linalg.norm(reference[x] - query[wq][x])
                query_dist_capped += min(capped_distance, .5)
            new_percentage = query_dist_capped/(.5 * alignment.M) * 100
            denum = 0
            for x in range(len(reference)):
                denum += np.linalg.norm(reference[x] - inverted_reference[x])
            inverted_percentage = alignment.distance / denum * 100
            good_or_bad = "Good" if inverted_percentage <= thresholds[key] else "Bad"
            good_or_bad_new = "Good" if new_percentage <= thresholds_new[key] else "Bad"
            result = {
                "Body Part": key,
                "Demo": i,
                "Inverted Percentage": 100 - inverted_percentage,
                "Good or Bad": good_or_bad,
                "New Percentage": 100  - new_percentage,
                "Good or Bad New": good_or_bad_new

            }
            results.append(result)
    
    return results

def main(task_name):
    folder_path = os.path.join('Scenic-main/src/scenic/simulators/unity/', task_name)
    patientID, mainTask, taskName = task_name.split("/")
    evaluation_results_path = 'Scenic-main/src/scenic/simulators/unity/'
    evaluation_results_path += patientID  + "/"
    os.makedirs(evaluation_results_path, exist_ok=True)
    evaluation_results_path += mainTask  + "/"
    os.makedirs(evaluation_results_path, exist_ok=True)
    evaluation_results_path += "evaluationResults"  + "/"
    # evaluation_results_path = 'Scenic-main/src/scenic/simulators/unity/evaluationResults'
    os.makedirs(evaluation_results_path, exist_ok=True)

    thresholds = {
        "headLocationData": 36.211748,
        "armUpperLocationData": 37.412619,
        "armLowerLocationData": 23.463914,
        "wristLocationData": 35.335300,
        "thumbDistalLocationData": 34.192930,
        "thumbProximalLocationData": 34.192930, 
        "thumbMetacarpalLocationData": 34.192930, 
        "indexDistalLocationData": 34.192930, 
        "indexProximalLocationData": 34.192930, 
        "indexMetacarpalLocationData": 34.192930, 
        "middleDistalLocationData": 34.192930, 
        "middleProximalLocationData": 34.192930, 
        "middleMetacarpalLocationData": 34.192930, 
        "ringDistalLocationData": 34.192930, 
        "ringProximalLocationData": 34.192930, 
        "ringMetacarpalLocationData": 34.192930, 
        "littleDistalLocationData": 34.192930, 
        "littleProximalLocationData": 34.192930, 
        "littleMetacarpalLocationData": 34.192930, 
        "headLocationData": 34.192930, 
        "wristLocationData": 34.192930, 
        "armLowerLocationData": 34.192930, 
        "armUpperLocationData": 34.192930
    }

    thresholds_new = {
        "headLocationData": 16.520357,
        "armUpperLocationData": 22.685049,
        "armLowerLocationData": 15.456550,
        "wristLocationData": 19.165705,
        "thumbDistalLocationData": 19.416005,
        "thumbProximalLocationData": 19.416005, 
        "thumbMetacarpalLocationData": 19.416005, 
        "indexDistalLocationData": 19.416005, 
        "indexProximalLocationData": 19.416005, 
        "indexMetacarpalLocationData": 19.416005, 
        "middleDistalLocationData": 19.416005, 
        "middleProximalLocationData": 19.416005, 
        "middleMetacarpalLocationData": 19.416005, 
        "ringDistalLocationData": 19.416005, 
        "ringProximalLocationData": 19.416005, 
        "ringMetacarpalLocationData": 19.416005, 
        "littleDistalLocationData": 19.416005, 
        "littleProximalLocationData": 19.416005, 
        "littleMetacarpalLocationData": 19.416005, 
        "headLocationData": 19.416005, 
        "wristLocationData": 19.416005, 
        "armLowerLocationData": 19.416005, 
        "armUpperLocationData": 19.416005
    }

    results = calc_perc_df(folder_path, thresholds, thresholds_new)
    
    output_file = os.path.join(evaluation_results_path, f'{taskName}.json')
    with open(output_file, 'w') as json_file:
        json.dump(results, json_file, indent=4)
    
    print(f'Processing complete. Results saved to {output_file}.')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process trajectory data from JSON files.')
    parser.add_argument('task_name', type=str, help='Name of the task folder to process.')
    args = parser.parse_args()
    main(args.task_name)