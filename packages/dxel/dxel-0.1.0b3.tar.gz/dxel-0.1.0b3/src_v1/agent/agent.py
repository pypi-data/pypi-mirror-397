from src.llm.openai import OpenAIClient as llmClient
from src.utils import load_config
import os
from src.utils import localFileManager
from src.utils import  agentLocalConfig

class Agent:

    def __init__(self, llm_client : llmClient, io_manager :localFileManager, agent_config:agentLocalConfig,max_call = 5):

        self.agent_config = agent_config
        self.llm_model = llm_client
        self.max_call = max_call
        self.io_manager = io_manager

    def think(self,id,context_json_str):

        user_prompt = self.agent_config.user_prompt_template.format(
                input_json=context_json_str
            )

        for i in range(self.max_call):
            output = self.llm_model.system_user_completion(self.agent_config.system_prompt, user_prompt)

            validate_flag_dict = self.agent_config.validate_the_ouptut(output)
            if validate_flag_dict['validated_flag'] :
                break

        if validate_flag_dict['validated_flag'] == False:
            # output = {}
            output['id'] = id
            output['status'] = 'error'
            output['message'] = validate_flag_dict['message']
            self.io_manager.save_invalid_json(id,output)   

            return None

        if (output['status'] == 'success'):
            output['id'] = id
            output['request_count'] = i
            self.io_manager.save_success_json(id,output)
            return None
        
        if (output['statys'] == 'error'):
            output['id'] = id
            self.io_manager.save_error_json(id, output)
            return None


    # def validate_the_ouptut(self, agent_output):

    #     key_list = ['choice_code_match_status','choice','reason','key_evidence_elements']
    #     if agent_output['status'] == 'success':
    #         content = agent_output['content']
    #         if type(eval(content)) == dict:
    #             content_dict  = eval(content)
    #             if len(content_dict.keys()) != 4:
    #                 return False
    #             for k, v in content_dict.items():
    #                 if k not in key_list:
    #                     return False
    #                 if type(content_dict[k]) != str:
    #                     return False
    #                 if (k == 'choice_code_match_status'):
    #                     if (content_dict['choice_code_match_status'] not in ['DIFFERENT', 'SIMILAR']) :
    #                         return False
    #                 if (k == "choice"):
    #                     if (content_dict['choice'] not in ['WK', 'Incurate','Neither']) :
    #                         return False
    #             return True
    #         else:
    #             return False
    #     else:
    #         return True








