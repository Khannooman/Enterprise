from decimal import Decimal
from typing import Dict, Any, List

class DataSecurityWrapper:
    @staticmethod
    def anonymize_query_result(query_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Anonymize the query result before passing to LLM.
        
        Args:
            query_result (dict): Original query result with headers and data
        
        Returns:
            dict: Anonymized query result
        """
        if not query_result or 'data' not in query_result:
            return query_result

        # Create a copy to avoid modifying the original
        anonymized_result = query_result.copy()
        
        # Anonymize data
        anonymized_data = []
        for idx, row in enumerate(query_result['data'], 1):
            anonymized_row = {}
            for key, value in row.items():
                # Anonymize numeric values
                if isinstance(value, (int, float, Decimal)):
                    # Replace with a generic value pattern
                    anonymized_row[key] = float(f"{idx}.{idx}")
                # Anonymize string values
                elif isinstance(value, str):
                    # Replace with a generic identifier
                    anonymized_row[key] = f"item_{idx}"
                else:
                    anonymized_row[key] = value
            anonymized_data.append(anonymized_row)
        
        anonymized_result['data'] = anonymized_data
        
        return anonymized_result

    @staticmethod
    def generate_safe_statistics(query_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate safe, aggregated statistics from query result.
        
        Args:
            query_result (dict): Original query result
        
        Returns:
            dict: Safe statistics for LLM consumption
        """
        if not query_result or 'data' not in query_result:
            return {}

        # Compute safe statistics
        safe_stats = {
            'total_records': len(query_result['data']),
            'column_names': query_result['headers'],
            'numeric_columns': [
                col for col in query_result['headers'] 
                if any(isinstance(row.get(col), (int, float, Decimal)) for row in query_result['data'])
            ],
            'unique_value_counts': {},
            'numeric_column_stats': {}
        }

        # Detailed analysis of numeric columns
        for col in safe_stats['numeric_columns']:
            numeric_values = [
                row.get(col) for row in query_result['data'] 
                if isinstance(row.get(col), (int, float, Decimal))
            ]
            
            safe_stats['numeric_column_stats'][col] = {
                'min': float(min(numeric_values)) if numeric_values else None,
                'max': float(max(numeric_values)) if numeric_values else None,
                'average': float(sum(numeric_values) / len(numeric_values)) if numeric_values else None
            }

        # Count unique values for non-numeric columns
        for col in query_result['headers']:
            if col not in safe_stats['numeric_columns']:
                unique_values = set(
                    row.get(col) for row in query_result['data'] 
                    if not isinstance(row.get(col), (int, float, Decimal))
                )
                safe_stats['unique_value_counts'][col] = len(unique_values)

        return safe_stats

    @staticmethod
    def create_generalized_description(query_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a generalized, non-identifying description of the data.
        
        Args:
            query_result (dict): Original query result
        
        Returns:
            dict: Generalized data description
        """
        if not query_result or 'data' not in query_result:
            return {}

        # Analyze data types and ranges
        column_analyses = {}
        for col in query_result['headers']:
            values = [row.get(col) for row in query_result['data']]
            
            # Numeric column analysis
            if all(isinstance(v, (int, float, Decimal)) for v in values if v is not None):
                numeric_values = [v for v in values if v is not None]
                column_analyses[col] = {
                    'type': 'numeric',
                    'min': float(min(numeric_values)),
                    'max': float(max(numeric_values)),
                    'approximate_range_description': f"Values range from {min(numeric_values)} to {max(numeric_values)}"
                }
            
            # Categorical column analysis
            elif all(isinstance(v, str) for v in values if v is not None):
                column_analyses[col] = {
                    'type': 'categorical',
                    'unique_count': len(set(values)),
                    'sample_categories_count': 'Multiple distinct categories present'
                }

        return {
            'data_overview': {
                'total_records': len(query_result['data']),
                'columns': column_analyses
            }
        }

    @staticmethod
    def prepare_llm_input(
        query_result: Dict[str, Any], 
        strategy: str = 'anonymize'
    ) -> Dict[str, Any]:
        """
        Prepare LLM input with chosen security strategy
        
        Args:
            query_result (dict): Original query result
            strategy (str): Security strategy to apply
        
        Returns:
            dict: Secured data representation
        """
        strategies = {
            'anonymize': DataSecurityWrapper.anonymize_query_result,
            'statistics': DataSecurityWrapper.generate_safe_statistics,
            'description': DataSecurityWrapper.create_generalized_description
        }
        
        # Default to anonymization if strategy not found
        secure_data = strategies.get(strategy, DataSecurityWrapper.anonymize_query_result)(query_result)
        return secure_data