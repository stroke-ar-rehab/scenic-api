import zmq
import json
import logging
import os
from time import sleep
import subprocess
import re



def get_ip_from_json(filepath):
    try:
        with open(filepath) as json_file:
            data = json.load(json_file)
            ip = data.get("ip", "localhost")  # Default to localhost if not found
            return ip
    except FileNotFoundError:
        print(f"File {filepath} not found, using localhost")
        return "localhost"
    except json.JSONDecodeError:
        print(f"Error decoding JSON from {filepath}, using localhost")
        return "localhost"

current_ip = get_ip_from_json("Scenic-main/src/scenic/simulators/unity/req.json")
sendPort = 5556
receivePort = 5557

class JsonSender:
    def __init__(self, ip, port, filepath):
        self.ip = ip
        self.port = port
        with open(filepath) as json_file:
            data = json.load(json_file)
        if isinstance(data, (dict, list)):
            self.dataToSend = data
        else:
            self.dataToSend = {"error": 0}
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUSH)
        self.address = f"tcp://{ip}:{port}"
        self.socket.connect(self.address)

    def sendData(self):
        try:
            json_data = json.dumps(self.dataToSend)
            self.socket.send_string(json_data)
            print("Data sent")
        except zmq.ZMQError as e:
            print(f"Failed to send data: {e}")



class JsonReceiver:
    processed_folders = set()

    def __init__(self, ip, port):
        context = zmq.Context()
        self.socket = context.socket(zmq.PULL)
        self.address = f"tcp://{ip}:{port}"
        self.socket.setsockopt(zmq.RCVTIMEO, 10000)  # 10 seconds timeout for receiving
        self.socket.setsockopt(zmq.SNDTIMEO, 10000) 
        self.socket.connect(self.address)
        self.taskName = ""
        logging.info(f"Server started at {self.address}")

    def runServer(self):
        while True:
            try:
                # Poll the socket for incoming messages
                if self.socket.poll(timeout=1000):  # timeout in milliseconds
                    message = self.socket.recv_string()
                    
                    # Patient Record
                    splited_message = message.split("|")
                    isPatientRecord = False
                    if len(splited_message) == 4 :
                        patientID, mainTask, taskName, jsonContent = splited_message
                        logging.info(f"Received message: Recording")   
                        isPatientRecord = True
                        
                    # Joint angles or Quaternions data
                    if not isPatientRecord:
                        patientID, mainTask, taskName, whichSide, subtask,jsonContent = splited_message
                    logging.info(f"Received message: {patientID}, {mainTask}, {taskName}")

                    # self.dtwPath = patientID + "/" + mainTask + "/" +taskName
                    folder_path = 'Scenic-main/src/scenic/simulators/unity/' + patientID
                    if not os.path.exists(folder_path):
                        os.makedirs(folder_path)
                        logging.info(f"Created directory {folder_path}")    
                    
                    folder_path += "/" + mainTask
                    
                    if not os.path.exists(folder_path):
                        os.makedirs(folder_path)
                        logging.info(f"Created directory {folder_path}")    
                        
                    if isPatientRecord :
                        file_path = os.path.join(folder_path, taskName)
                        file_path += ".json"
                        if isinstance(jsonContent, str):
                            jsonContent = json.loads(jsonContent)
                        with open(file_path, 'w') as json_file:
                            json.dump(jsonContent, json_file, indent=4)
                            logging.info(f"Saved JSON to {file_path}")
                        continue
                        
                    folder_path += "/" + taskName
                    
                    if not os.path.exists(folder_path):
                        os.makedirs(folder_path)
                        logging.info(f"Created directory {folder_path}")    
                        
                    folder_path += "/" + subtask
                    
                    if not os.path.exists(folder_path):
                        os.makedirs(folder_path)
                        logging.info(f"Created directory {folder_path}")    
                    
                    base_file_path = os.path.join(folder_path, taskName + whichSide)
                    counter = 0
                    file_path = base_file_path + "_" + str(counter) + '.json'
                    while os.path.exists(file_path):
                        counter += 1
                        file_path = f"{base_file_path}_{counter}.json"
                    
                    if isinstance(jsonContent, str):
                        jsonContent = json.loads(jsonContent)
                    with open(file_path, 'w') as json_file:
                        json.dump(jsonContent, json_file)
                        logging.info(f"Saved JSON to {file_path}")
                    
                else:
                    logging.info("No message received within timeout period")
            except zmq.ZMQError as e:
                logging.error(f"ZMQ Error: {e}")
                sleep(1)  # wait for a second before retrying
            except Exception as e:
                logging.error(f"An error occurred: {e}")
    
    # def check_folder(self, folder_path):
        
    #     if os.path.isdir(folder_path):
    #         files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    #         if len(files) >= 2:
    #             logging.info(f"Found enough files in {folder_path} to run dtw_location")
    #             self.run_dtw_location(folder_path)
    #         else:
    #             logging.info(f"Not enough files in the folder {folder_path}")
    #     else:
    #         logging.warning(f"Folder path {folder_path} is not a directory")

    # def check_folders(self, watch_dir):
    #     for folder in os.listdir(watch_dir):
    #         folder_path = os.path.join(watch_dir, folder)
    #         if os.path.isdir(folder_path):
    #             files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
    #             if len(files) >= 2:
    #                 self.run_dtw_location(folder)

    # def run_dtw_location(self, folder_name):
    #     logging.info(f"Running dtw_location.py for {folder_name}")
    #     task_name = os.path.basename(folder_name)
    #     #for windows
    #     #python_executable = os.path.join(os.getcwd(), 'venv', 'Scripts', 'python')
    #     #for mac
    #     python_executable = 'python3'
    #     print("Folder name for dtw is :",folder_name)
    #     evaluation_results_path = os.path.join('evaluationResults')
    #     os.makedirs(evaluation_results_path, exist_ok=True)
    
    #     try:
    #         result = subprocess.run([python_executable, 'Scenic-main/src/scenic/simulators/unity/dtw_location.py', self.dtwPath], capture_output=True, text=True, check=True)
    #         if result.returncode == 0:
    #             logging.info(f"dtw_location.py ran successfully for {folder_name}")
                
    #             output_file = os.path.join('evaluationResults', f'{task_name}.json')
    #             if os.path.exists(output_file):
    #                 sender = JsonSender(current_ip, sendPort, output_file)
    #                 sender.sendData()
    #         else:
    #             logging.error(f"Error running dtw_location.py for {folder_name}")
    #             logging.error(result.stderr)
    #     except subprocess.CalledProcessError as e:
    #         logging.error(f"Subprocess error: {e}")
    #         logging.error(f"Output: {e.output}")
    #         logging.error(f"Error output: {e.stderr}")

def testReceive():
    logging.basicConfig(level=logging.INFO)
    testReceiver = JsonReceiver(current_ip, "5557")
    testReceiver.runServer()

# if __name__ == "__main__":
#     testReceive()

def testSendingData():
    
    testSender = JsonSender(current_ip, "5556", "Scenic-main/src/scenic/simulators/unity/evaluationResults/SittingOrangeFruitBox1.json")
    testSender.sendData()  
    


# Run the test

# testSendingData()
testReceive()