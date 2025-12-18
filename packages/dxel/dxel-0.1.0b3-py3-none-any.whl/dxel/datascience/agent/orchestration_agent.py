from dxel.datascience.utils import summarize_df
from dxel.utils.llm_agent.agent import Agent
from dxel.utils.llm.gemini import Gemini
import pandas as pd
import io
import base64
import matplotlib.pyplot as plt


class DataAnalystAgent :

    def __init__(self, llm ,df_loc=None, df=None):
        """
        Initialize DataAnalystAgent with either a CSV file path or a DataFrame.
        
        Args:
            df_loc (str, optional): Path to CSV file
            api_key (str): Google API key for Gemini
            df (pd.DataFrame, optional): Pandas DataFrame directly
        
        Note: Either df_loc or df must be provided (not both)
        """
        if df is not None:
            self.df = df
        elif df_loc is not None:
            self.df = pd.read_csv(df_loc)
        else:
            raise ValueError("Either df_loc or df must be provided")
        
        self.summary_json = summarize_df(self.df)
        self.gemini_llm = llm
        self.summary_agent = self._create_summary_agent()
        self.plot_agent = self._create_plot_agent()
        self.router_agent =  self._router_agent()
    
    def update_dataframe(self, df_loc=None, df=None):
        """
        Update the DataFrame being analyzed.
        
        Args:
            df_loc (str, optional): Path to new CSV file
            df (pd.DataFrame, optional): New pandas DataFrame
        """
        if df is not None:
            self.df = df
        elif df_loc is not None:
            self.df = pd.read_csv(df_loc)
        else:
            raise ValueError("Either df_loc or df must be provided")
        
        # Regenerate summary and agents with new data
        self.summary_json = summarize_df(self.df)
        self.summary_agent = self._create_summary_agent()
        self.plot_agent = self._create_plot_agent()
        self.router_agent = self._router_agent()


    def think(self, user_prompt, chatbot = False):
        """
        Process user prompt and return response.
        
        Args:
            user_prompt: User's question
            return_type: 'auto' (exec for plots), 'text' (text response), or 'plot_data' (returns plot as base64)
        
        Returns:
            For text queries: string response
            For plot queries with return_type='auto': None (executes plt.show())
            For plot queries with return_type='plot_data': dict with 'type' and 'data' (base64 image)
        """
        agent_choice = self.router_agent.think(user_prompt)

        if (agent_choice not in ['1','2']):
            if chatbot:
                return  {"type":"text" , "data":"I could not understand your question"}
            else:
                print("I could not understand your question")

        if agent_choice == '1':
            response = self.summary_agent.think(user_prompt)
            if chatbot:
                return {"type":"text" , "data":response}
            else:
                print(response)
        
        if agent_choice == '2':
            output = self.plot_agent.think(user_prompt)

            if ((output[0:10]  == '```python\n') and (output[-4:] == '\n```')):
                code = output[10:-4]
            else:
                code = output

            if chatbot:            
                exec(code)
                
                buf = io.BytesIO()
                plt.savefig(buf, format='png', bbox_inches='tight', dpi=100)
                plt.close('all')
                buf.seek(0)
                
                img_base64 = base64.b64encode(buf.read()).decode('utf-8')
                return {"type": "plot", "data": img_base64}
            
            else:
                exec(code)


    def _router_agent(self):

        system_prompt_template = """
        
        You are an agent router. You have metadata for a pandas DataFrame in JSON format:
        
        {df_meta_json}
        
        You have two specialist agents:
        1) summary_agent — answers factual or statistical questions using ONLY the provided metadata (no code, no access to row-level data). Use this when the question can be resolved from metadata (e.g., column types, counts, missing values, basic summary stats).
        2) plot_agent — returns Python (matplotlib) code that creates a plot using the pandas DataFrame variable named df. Use this when the question requests a visualization or requires inspecting/visualizing row-level data.

        Task:
        - Read the user's question below and choose which agent to trigger.
        - If summary_agent is appropriate, output exactly: 1
        - If plot_agent is appropriate, output exactly: 2
        - Output must be only the single character "1" or "2" with no extra text, punctuation, whitespace, or explanation.

        Decision guidance (examples):
        - Use 1 (summary_agent) for questions like:
        - "How many missing values are in column X?"
        - "What are the data types and unique counts for each column?"
        - "What is the mean and median of column Y?"
        - Use 2 (plot_agent) for questions like:
        - "Show a histogram of column X."
        - "Plot sales over time by region."
        - "Compare distributions of columns A and B."
        """

        system_prompt = system_prompt_template.format(
            df_meta_json= self.summary_json
        )

        agent_config = {
            'system_prompt' : system_prompt
        }
        return Agent(self.gemini_llm, agent_config)



    def _create_summary_agent(self ):

        system_prompt_template = """
        You have been provided with metadata for a pandas DataFrame as follows:
        {df_meta_json}
        Using this metadata, answer the following question:
        """

        system_prompt = system_prompt_template.format(
            df_meta_json= self.summary_json
        )

        agent_config = {
            'system_prompt' : system_prompt
            }
        
        return Agent(self.gemini_llm, agent_config)

    def _create_plot_agent(self):

        system_prompt_template = """
            You have been provided with metadata for a pandas DataFrame as follows:
            {df_meta_json}
            Using this metadata, produce Python (matplotlib) code to generate the requested plot.
            Requirements:
            - The DataFrame is available as df; reference it using self.df (the variable is already defined).
            - Output must be ONLY valid Python code (no explanations, no markdown, no backticks).
            - Do NOT include imports for pandas, matplotlib.pyplot as they are already available as pd and plt respectively.
            - Validate that any referenced columns exist in df; if a required column is missing, raise a ValueError with a clear message.
            - Do not read external files or assume values not present in the provided metadata.
            - Do not call plt.show() at the end, just create the plot.
            """


        system_prompt = system_prompt_template.format(
            df_meta_json= self.summary_json
        )

        agent_config = {
            'system_prompt' : system_prompt
            }
        
        return Agent(self.gemini_llm, agent_config)




