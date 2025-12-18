"""
Test script to verify dynamic CSV loading functionality
"""
import os
import sys
import pandas as pd
from dotenv import load_dotenv

# Project setup
project_name = 'DataGenie'
base_pth = os.getcwd().split(project_name)[0] + f'{project_name}/'
sys.path.append(base_pth)


from dxel.datascience.agent import DataAnalystAgent
from dxel.utils.llm.gemini import Gemini

# Load environment variables
load_dotenv()
api_key = os.getenv('GOOGLE_API_KEY')
gemini_llm = Gemini(api_key=api_key)

def test_csv_path_init():
    """Test initialization with CSV file path"""
    print("=" * 60)
    print("Test 1: Initialize with CSV file path")
    print("=" * 60)
    
    data_loc = base_pth + 'notebook_io/data_agent/input/Titanic-Dataset.csv'
    agent = DataAnalystAgent(gemini_llm, df_loc=data_loc)
    
    print(f"✅ Agent initialized with CSV file")
    print(f"   Dataset shape: {agent.df.shape}")
    print(f"   Columns: {list(agent.df.columns)[:5]}...")
    print()

def test_dataframe_init():
    """Test initialization with DataFrame directly"""
    print("=" * 60)
    print("Test 2: Initialize with DataFrame")
    print("=" * 60)
    
    # Create a sample DataFrame
    df = pd.DataFrame({
        'name': ['Alice', 'Bob', 'Charlie'],
        'age': [25, 30, 35],
        'score': [85.5, 92.3, 78.9]
    })
    
    agent = DataAnalystAgent(gemini_llm, df=df)
    
    print(f"✅ Agent initialized with DataFrame")
    print(f"   Dataset shape: {agent.df.shape}")
    print(f"   Columns: {list(agent.df.columns)}")
    print(f"   Sample data:\n{agent.df.head()}")
    print()

def test_update_dataframe():
    """Test updating the DataFrame after initialization"""
    print("=" * 60)
    print("Test 3: Update DataFrame dynamically")
    print("=" * 60)
    
    # Initial DataFrame
    df1 = pd.DataFrame({
        'product': ['A', 'B', 'C'],
        'price': [10, 20, 30]
    })
    
    agent = DataAnalystAgent(gemini_llm, df=df1)
    print(f"Initial dataset shape: {agent.df.shape}")
    print(f"Initial columns: {list(agent.df.columns)}")
    
    # Update with new DataFrame
    df2 = pd.DataFrame({
        'city': ['NYC', 'LA', 'Chicago', 'Houston'],
        'population': [8000000, 4000000, 2700000, 2300000],
        'area_sqmi': [302, 469, 227, 637]
    })
    
    agent.update_dataframe(df=df2)
    print(f"\n✅ Dataset updated!")
    print(f"   New dataset shape: {agent.df.shape}")
    print(f"   New columns: {list(agent.df.columns)}")
    print(f"   Sample data:\n{agent.df.head()}")
    print()

def test_error_handling():
    """Test error handling for missing parameters"""
    print("=" * 60)
    print("Test 4: Error handling for missing parameters")
    print("=" * 60)
    
    try:
        agent = DataAnalystAgent(gemini_llm)
        print("❌ Should have raised ValueError")
    except ValueError as e:
        print(f"✅ Correctly raised ValueError: {e}")
    print()

if __name__ == "__main__":
    print("\n🧪 Testing Dynamic CSV Loading Functionality\n")
    
    test_csv_path_init()
    test_dataframe_init()
    test_update_dataframe()
    test_error_handling()
    
    print("=" * 60)
    print("✅ All tests completed!")
    print("=" * 60)
