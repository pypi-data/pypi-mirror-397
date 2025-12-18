from sfn_blueprint.utils.logging import setup_logger

class DataAnalyzer:
    """
    Tool for comprehensive data analysis and profiling.
    
    This tool analyzes pandas DataFrames and generates detailed summaries
    including shape, data types, missing values, duplicates, and statistical
    summaries for both numeric and categorical columns.
    
    Provides insights essential for data understanding and preprocessing.
    """
    
    def __init__(self):
        """
        Initialize the Data Analyzer tool.
        
        Sets up the tool with logging capabilities for tracking
        analysis operations and results.
        """
        self.logger, _ = setup_logger(logger_name="DataAnalyzer")

    def analyze(self, task):
        """
        Analyze the provided DataFrame and return comprehensive summary.
        
        Generates detailed statistics and insights about the dataset including
        structure, data types, missing values, duplicates, and statistical summaries
        for numeric and categorical columns.

        Args:
            task: Task object containing:
                - data (pd.DataFrame): DataFrame to analyze

        Returns:
            dict: Comprehensive data summary containing:
                - shape (tuple): DataFrame dimensions
                - columns (list): Column names
                - dtypes (dict): Column data types
                - missing_values (dict): Missing value counts per column
                - duplicates (int): Number of duplicate rows
                - numeric_summary (dict): Statistical summary for numeric columns
                - categorical_summary (dict): Summary for categorical columns

        Raises:
            Exception: If data analysis encounters errors

        Note:
            Handles empty categorical columns gracefully by returning empty dict.
        """
        df = task.data
        self.logger.info("Starting data analysis...")
        
        try:
            # Log the shape and column names
            self.logger.info(f"DataFrame shape: {df.shape}")
            self.logger.info(f"Columns: {df.columns.tolist()}")

            # Generate summaries
            data_summary = {
                "shape": df.shape,
                "columns": df.columns.tolist(),
                "dtypes": df.dtypes.to_dict(),
                "missing_values": df.isnull().sum().to_dict(),
                "duplicates": df.duplicated().sum(),
                "numeric_summary": df.describe().to_dict()
            }

            # Handle categorical columns
            categorical_columns = df.select_dtypes(include=['object'])
            if not categorical_columns.empty:
                data_summary["categorical_summary"] = categorical_columns.describe().to_dict()
            else:
                self.logger.info("No categorical columns to describe.")
                data_summary["categorical_summary"] = {}

            self.logger.info("Data analysis completed successfully.")
            return data_summary
        except Exception as e:
            self.logger.error(f"Error during data analysis: {str(e)}")
            raise e
