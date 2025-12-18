import json
import os
from .utils import read_json_file
import yaml


        
class agentLocalConfig:
    def __init__(self, config_name, config_path):
        self.config_location = os.path.join(config_path,config_name)
        self.agent_config = read_json_file(os.path.join(self.config_location,'agent_config.json'))
        self.prompt_loc = os.path.join(config_path,config_name,'prompt.yaml')
        self.prompt_config = self.load_prompt(self.prompt_loc,["system_prompt_template", "user_prompt_template"])
        self.system_prompt_template = self.prompt_config['system_prompt_template']
        self.user_prompt_template = self.prompt_config['user_prompt_template']
        self.output_json_structure = self.get_agent_io_string_structure(self.agent_config['output_json_structure'])
        self.input_json_structure = self.get_agent_io_string_structure(self.agent_config['input_json_structure'])
        
        # Beautify the input and output JSON structures for better readability
        beautified_input_json_structure = json.dumps(self.input_json_structure, indent=4)
        beautified_output_json_structure = json.dumps(self.output_json_structure, indent=4)
        
        self.system_prompt = self.system_prompt_template.format(
            Input_json_structure=beautified_input_json_structure,
            Output_json_structure=beautified_output_json_structure
        )

    def load_prompt(self,config_path, required_keys):
        try:
            with open(config_path, "r") as f:
                config = yaml.safe_load(f)
            if not isinstance(config, dict):
                raise ValueError("Config file is not a valid YAML dictionary.")
            for key in required_keys:
                if key not in config:
                    raise KeyError(f"Missing required config key: {key}")
            return config
        except Exception as e:
            raise RuntimeError(f"Error loading config: {str(e)}")
        

    def leaf_node_return(self,node_dict):
        if node_dict['output_type'] == 'text':
            return f"<{node_dict['description']}>"
        elif node_dict['output_type'] == 'text_choice':
            return f"<{' or '.join(node_dict['choice_list'])}>"
        else:
            raise Exception(f"Check output type, {node_dict['output_type']} is not standard output type.")

    def get_agent_io_string_structure(self,tree_dict):
        leaf_node_flag = tree_dict.get('leaf_node',"False")
        if leaf_node_flag == 'True':
            return self.leaf_node_return(tree_dict)
        else:
            return_dict = {}
            for key,value in tree_dict.items():
                if (key != "leaf_node"):
                    if isinstance(value,dict):
                        return_dict[key] = self.get_agent_io_string_structure(value)
                    else:
                        return_dict[key] 
            return return_dict
          

    def validate_the_ouptut(self, agent_output):
        if agent_output['status'] == 'success':
            content = agent_output['content']
            if content.startswith("```json\n") and content.endswith("\n```"):
                content = content[8:-4]
            if type(eval(content)) == dict:
                content = eval(content)
                content_keys = set(content.keys())
                output_keys = set(self.agent_config['output_json_structure'].keys())
                output_keys.discard('leaf_node')

                if (content_keys != output_keys):

                    return {
                        "validated_flag": False,
                        "message" : "output keys are not same"
                    }
                for key in output_keys:
                    if self.agent_config['output_json_structure'][key]['output_type'] == 'text_choice':

                        if (content[key] not in self.agent_config['output_json_structure'][key]['choice_list']):
                            return {
                                "validated_flag": False,
                                "message" : f"{content[key]} is not part of {self.agent_config['output_json_structure'][key]['choice_list']} "
                                }
                        
                return {
                        "validated_flag": True,
                        "message" : "Output is valid"
                    }
            
            else:
                 return {
                                "validated_flag": False,
                                "message" : f"output is not standard dict {content}"
                    }
        else:
            return {
                "validated_flag": True,
                "message" : f"llm output was not standard"
            }




                    









                    

                





        








