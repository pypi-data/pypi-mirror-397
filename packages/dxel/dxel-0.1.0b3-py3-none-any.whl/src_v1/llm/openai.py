import openai
from typing import Optional, Dict, Any, List
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class OpenAIClient:
    
    def __init__(self,api_key:str, api_endpoint:str, openai_gpt_engine:str, temp = 0):

        self.api_key = api_key
        self.api_endpoint = api_endpoint

        if not self.api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass api_key parameter.")
        
        self.model = openai_gpt_engine
        self.client = openai.OpenAI(api_key=self.api_key,
                                    base_url=self.api_endpoint)
        self.temperature = temp
    
    def chat_completion(
        self, 
        messages: List[Dict[str, str]], 

    ) :
        try:

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature
            )

            if response and hasattr(response, 'choices') and response.choices:

                usage_dict = dict(response.usage)
                return {
                    "status" : "success",
                    "content" : response.choices[0].message.content,
                    "model" : response.model,
                    "prompt_tokens" :  usage_dict["prompt_tokens"],
                    "completion_tokens" : usage_dict["completion_tokens"],
                    "total_tokens" : usage_dict["total_tokens"],
                    "finish_reason" : response.choices[0].finish_reason
                }
            elif response and hasattr(response, 'error') and response.error:
                return {
                    "status" : "error",
                    "message" : response.error.message,
                }
            else:
                return {
                    "status" : "error",
                    "message" : "error  or choices not part of response"
                }

        except Exception as e:
            return {
                "status" : "error",
                "message" : str(e),
                }

    

    def simple_completion(
        self, 
        prompt: str, 
    ) :
        messages = [{"role": "user", "content": prompt}]
        return self.chat_completion(messages)
    
    def system_user_completion(
        self,
        system_message: str,
        user_message: str
    ) :

        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]
        return self.chat_completion(messages)
    
