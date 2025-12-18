from dxel.utils.llm.base_llm import BaseLLM as llmClient

class Agent:

    def __init__(self, llm_client : llmClient, agent_config):
        self.agent_config = agent_config
        self.llm_model = llm_client

    def think(self,user_prompt):

        # user_prompt = self.agent_config.user_prompt_template.format(
        #         input_json=context_json_str
        #     )

        output = self.llm_model.generate( user_prompt, self.agent_config['system_prompt'])

        return output



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








