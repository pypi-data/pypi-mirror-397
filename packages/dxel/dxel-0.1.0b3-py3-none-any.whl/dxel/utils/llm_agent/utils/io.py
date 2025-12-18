# import pandas as pd
# import os
# import shutil
# import json

# class localFileManager:

#     """
#     This class handles file management for local runs.
#     It retrieves input data from the 'input_data' directory in the root
#     and manages all intermediate and final outputs in the 'data' directory in the root.
#     """
#     def __init__(self, execution_id):
#         base_path = os.getcwd().split("loinc_agent")[0]
#         self.base_dir_path = os.path.join(base_path, "loinc_agent", "data")
#         self.execution_id = execution_id


#     def save_success_json(self,id,succee_dict):

#         output_dir_pth = os.path.join(
#             self.base_dir_path,
#             "agent_output",
#             str(self.execution_id),
#             "success",
#         )

#         os.makedirs(output_dir_pth, exist_ok=True) 

#         filename = f'{id}.json'

#         with open(os.path.join(output_dir_pth,filename), "w") as f:
#                     json.dump(succee_dict, f, indent=2)

#     def save_error_json(self,id,error_dict):

#         output_dir_pth = os.path.join(
#             self.base_dir_path,
#             "agent_output",
#             str(self.execution_id),
#             "error",
#         )

#         os.makedirs(output_dir_pth, exist_ok=True) 

#         filename = f'{id}.json'

#         with open(os.path.join(output_dir_pth,filename), "w") as f:
#                     json.dump(error_dict, f, indent=2)


#     def save_invalid_json(self,id,invalid_dict):

#         output_dir_pth = os.path.join(
#             self.base_dir_path,
#             str(self.execution_id),
#             "agent_output",
#             "invalid",
#         )

#         os.makedirs(output_dir_pth, exist_ok=True) 

#         filename = f'{id}.json'

#         with open(os.path.join(output_dir_pth,filename), "w") as f:
#                     json.dump(invalid_dict, f, indent=2)


#     def load_json_to_df(self):
           
#         input_dir_pth = os.path.join(
#             self.base_dir_path,
#             "agent_output",
#             str(self.execution_id),
#             "success",
#         )

#         os.makedirs(input_dir_pth, exist_ok=True) 
#         rows = []
#         for file in os.listdir(input_dir_pth):
#             if file.endswith(".json"):
#                 with open(os.path.join(input_dir_pth, file), "r") as f:
#                     data = json.load(f)
#             rows.append(data)
#         df = pd.DataFrame(rows)
#         return df
        

