import json
import os
import glob
from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
import numpy as np
from datetime import datetime

class SalesSimulationData:
    """Class to load and process sales simulation test results data."""
    
    def __init__(self, test_results_dir: str = "../test-results"):
        """Initialize the data loader with the path to the test results directory."""
        self.test_results_dir = test_results_dir
        self.summary_data = None
        self.simulation_results = None
        self.conversation_data = None
        self.detailed_results = None
        self.historical_results = []
        self.load_data()
    
    def load_data(self) -> None:
        """Load all data from the test results directory."""
        # Load summary data
        summary_path = os.path.join(self.test_results_dir, "latest-simulation-summary.json")
        if os.path.exists(summary_path):
            with open(summary_path, 'r') as f:
                self.summary_data = json.load(f)
        
        # Load simulation results
        results_path = os.path.join(self.test_results_dir, "simulation-results.json")
        if os.path.exists(results_path):
            with open(results_path, 'r') as f:
                data = json.load(f)
                self.simulation_results = data.get('results', [])
        
        # Load conversation data
        conversation_path = os.path.join(self.test_results_dir, "conversation-data.json")
        if os.path.exists(conversation_path):
            with open(conversation_path, 'r') as f:
                self.conversation_data = json.load(f)
        
        # Load detailed results (most recent)
        detailed_results_files = glob.glob(os.path.join(self.test_results_dir, "sales-simulation-results-*.json"))
        if detailed_results_files:
            # Sort by modification time (newest first)
            detailed_results_files.sort(key=os.path.getmtime, reverse=True)
            with open(detailed_results_files[0], 'r') as f:
                self.detailed_results = json.load(f)
        
        # Load historical results
        for file_path in detailed_results_files:
            with open(file_path, 'r') as f:
                data = json.load(f)
                # Extract timestamp from filename
                filename = os.path.basename(file_path)
                timestamp = filename.replace("sales-simulation-results-", "").replace(".json", "")
                data['file_timestamp'] = timestamp
                self.historical_results.append(data)
        
        # Sort historical results by timestamp
        self.historical_results.sort(key=lambda x: x.get('file_timestamp', ''), reverse=True)
    
    def get_summary_stats(self) -> Dict[str, Any]:
        """Get summary statistics from the latest test run."""
        if not self.summary_data:
            return {}
        
        return {
            'total_simulations': self.summary_data.get('totalSimulations', 0),
            'passed_simulations': self.summary_data.get('passedSimulations', 0),
            'pass_rate': self.summary_data.get('passRate', '0%'),
            'timestamp': self.summary_data.get('timestamp', ''),
            'duration': self.summary_data.get('duration', 0),
            'test_run_date': self.summary_data.get('testRunDate', ''),
            'test_run_time': self.summary_data.get('testRunTime', '')
        }
    
    def get_simulation_results_df(self) -> pd.DataFrame:
        """Convert simulation results to a pandas DataFrame."""
        if not self.simulation_results:
            return pd.DataFrame()
        
        df = pd.DataFrame(self.simulation_results)
        
        # Convert duration from milliseconds to seconds
        if 'duration' in df.columns:
            df['duration_seconds'] = df['duration'] / 1000
        
        return df
    
    def get_conversation_by_simulation_id(self, simulation_id: int) -> List[Dict[str, str]]:
        """Get conversation data for a specific simulation."""
        if not self.conversation_data:
            return []
        
        for sim in self.conversation_data:
            if sim.get('simulationNumber') == simulation_id:
                return sim.get('conversation', [])
        
        return []
    
    def get_conversation_df(self, simulation_id: int) -> pd.DataFrame:
        """Get conversation data as a DataFrame for a specific simulation."""
        conversation = self.get_conversation_by_simulation_id(simulation_id)
        if not conversation:
            return pd.DataFrame()
        
        df = pd.DataFrame(conversation)
        df['message_length'] = df['message'].apply(len)
        df['turn_number'] = range(1, len(df) + 1)
        
        return df
    
    def get_all_simulations_metadata(self) -> pd.DataFrame:
        """Get metadata for all simulations."""
        if not self.conversation_data:
            return pd.DataFrame()
        
        metadata = []
        for sim in self.conversation_data:
            metadata.append({
                'simulation_id': sim.get('simulationNumber'),
                'start_index': sim.get('startIndex'),
                'duration': sim.get('duration', 0) / 1000,  # Convert to seconds
                'conversation_length': len(sim.get('conversation', [])),
                'passed': sim.get('evaluation', {}).get('overallPassed', False),
                'sales_agent_passed': sim.get('evaluation', {}).get('salesAgentPassed', False),
                'customer_agent_passed': sim.get('evaluation', {}).get('customerAgentPassed', False)
            })
        
        return pd.DataFrame(metadata)
    
    def get_historical_pass_rates(self) -> pd.DataFrame:
        """Get historical pass rates from all test runs."""
        if not self.historical_results:
            return pd.DataFrame()
        
        data = []
        for result in self.historical_results:
            summary = result.get('summary', {})
            timestamp = result.get('file_timestamp', '')
            try:
                # Convert timestamp to datetime
                dt = datetime.strptime(timestamp, "%Y-%m-%dT%H-%M-%S-%fZ")
                formatted_date = dt.strftime("%Y-%m-%d %H:%M")
            except:
                formatted_date = timestamp
                
            data.append({
                'timestamp': formatted_date,
                'total_simulations': summary.get('totalSimulations', 0),
                'passed_simulations': summary.get('passedSimulations', 0),
                'pass_rate': float(summary.get('passRate', '0%').replace('%', '')),
                'duration': summary.get('duration', 0)
            })
        
        return pd.DataFrame(data)
    
    def get_feedback_data(self) -> Tuple[List[str], List[str]]:
        """Extract sales agent and customer agent feedback."""
        if not self.simulation_results:
            return [], []
        
        sales_feedback = [result.get('salesAgentFeedback', '') for result in self.simulation_results]
        customer_feedback = [result.get('customerAgentFeedback', '') for result in self.simulation_results]
        
        return sales_feedback, customer_feedback
    
    def get_conversation_stats(self) -> pd.DataFrame:
        """Calculate statistics for all conversations."""
        if not self.conversation_data:
            return pd.DataFrame()
        
        stats = []
        for sim in self.conversation_data:
            conversation = sim.get('conversation', [])
            if not conversation:
                continue
                
            # Count messages by agent
            sales_messages = [msg for msg in conversation if msg.get('agent') == 'Sales Agent']
            customer_messages = [msg for msg in conversation if msg.get('agent') == 'Customer']
            
            # Calculate message lengths
            sales_lengths = [len(msg.get('message', '')) for msg in sales_messages]
            customer_lengths = [len(msg.get('message', '')) for msg in customer_messages]
            
            stats.append({
                'simulation_id': sim.get('simulationNumber'),
                'total_messages': len(conversation),
                'sales_messages': len(sales_messages),
                'customer_messages': len(customer_messages),
                'avg_sales_length': np.mean(sales_lengths) if sales_lengths else 0,
                'avg_customer_length': np.mean(customer_lengths) if customer_lengths else 0,
                'max_sales_length': max(sales_lengths) if sales_lengths else 0,
                'max_customer_length': max(customer_lengths) if customer_lengths else 0,
                'conversation_duration': sim.get('duration', 0) / 1000  # Convert to seconds
            })
        
        return pd.DataFrame(stats)


# Example usage
if __name__ == "__main__":
    data_loader = SalesSimulationData()
    summary = data_loader.get_summary_stats()
    print("Summary Stats:", summary)
    
    sim_results = data_loader.get_simulation_results_df()
    print("\nSimulation Results:")
    print(sim_results.head())
    
    if not sim_results.empty:
        first_sim_id = sim_results.iloc[0]['simulationNumber']
        conversation = data_loader.get_conversation_by_simulation_id(first_sim_id)
        print(f"\nFirst conversation (Simulation #{first_sim_id}):")
        for i, msg in enumerate(conversation[:3]):  # Print first 3 messages
            print(f"{i+1}. {msg['agent']}: {msg['message'][:50]}...") 