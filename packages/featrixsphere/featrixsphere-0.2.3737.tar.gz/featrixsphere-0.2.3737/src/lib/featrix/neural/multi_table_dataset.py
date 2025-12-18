#  -*- coding: utf-8 -*-
#
#  Copyright Featrix, Inc 2023-2025
#
#  Proprietary and Confidential.  Unauthorized use, copying or dissemination
#  of these materials is strictly prohibited.
#
"""
Multi-table dataset for GraphEncoder that manages multiple related tables with shared keys.
"""
import logging
from typing import Dict, List, Optional, Tuple

import pandas as pd
import torch

from featrix.neural.featrix_token import TokenBatch, Token, TokenStatus

logger = logging.getLogger(__name__)


class MultiTableDataset:
    """
    Container for multiple related tables with shared keys.
    
    Manages:
    - Multiple DataFrames (one per table)
    - Shared key mappings between tables
    - Relationship types (1:1, 1:N, N:M)
    - Batch generation for training
    """
    
    def __init__(
        self,
        tables: Dict[str, pd.DataFrame],
        shared_keys: Dict[Tuple[str, str], List[str]],
        relationship_types: Dict[Tuple[str, str], str],
        codecs: Optional[Dict[str, Dict[str, any]]] = None,
    ):
        """
        Initialize multi-table dataset.
        
        Args:
            tables: Dict mapping table names to DataFrames
            shared_keys: Dict mapping (table_a, table_b) to list of shared key column names
            relationship_types: Dict mapping (table_a, table_b) to relationship type ("1:1", "1:N", "N:M")
            codecs: Optional dict mapping table names to their column codecs
        """
        self.tables = tables
        self.shared_keys = shared_keys
        self.relationship_types = relationship_types
        self.codecs = codecs or {}
        
        # Validate shared keys exist in tables
        self._validate_shared_keys()
        
        # Pre-compute key indices for efficient matching
        self._key_indices: Dict[Tuple[str, str], Dict[Tuple, List[int]]] = {}
        self._precompute_key_indices()
    
    def _validate_shared_keys(self):
        """Validate that all shared keys exist in their respective tables."""
        for (table_a, table_b), keys in self.shared_keys.items():
            if table_a not in self.tables:
                raise ValueError(f"Table '{table_a}' not found in tables")
            if table_b not in self.tables:
                raise ValueError(f"Table '{table_b}' not found in tables")
            
            df_a = self.tables[table_a]
            df_b = self.tables[table_b]
            
            for key in keys:
                if key not in df_a.columns:
                    raise ValueError(f"Shared key '{key}' not found in table '{table_a}'")
                if key not in df_b.columns:
                    raise ValueError(f"Shared key '{key}' not found in table '{table_b}'")
    
    def _precompute_key_indices(self):
        """Pre-compute indices for efficient key matching."""
        for (table_a, table_b), keys in self.shared_keys.items():
            df_a = self.tables[table_a]
            df_b = self.tables[table_b]
            
            # Create index mapping: (key_values_tuple) -> [row_indices]
            index_map: Dict[Tuple, List[int]] = {}
            
            # Index table B by key values
            for idx_b, row_b in df_b.iterrows():
                key_values = tuple(row_b[k] for k in keys)
                if key_values not in index_map:
                    index_map[key_values] = []
                index_map[key_values].append(idx_b)
            
            self._key_indices[(table_a, table_b)] = index_map
    
    def get_table_size(self, table_name: str) -> int:
        """Get the number of rows in a table."""
        if table_name not in self.tables:
            raise ValueError(f"Table '{table_name}' not found")
        return len(self.tables[table_name])
    
    def get_related_indices(
        self,
        table_a: str,
        table_b: str,
        indices_a: List[int],
    ) -> List[List[int]]:
        """
        Get related indices in table_b for given indices in table_a.
        
        Args:
            table_a: Source table name
            table_b: Target table name
            indices_a: List of row indices in table_a
        
        Returns:
            List of lists, where each inner list contains indices in table_b related to corresponding index in indices_a
        """
        if (table_a, table_b) not in self.shared_keys:
            raise ValueError(f"No shared keys defined between '{table_a}' and '{table_b}'")
        
        keys = self.shared_keys[(table_a, table_b)]
        df_a = self.tables[table_a]
        index_map = self._key_indices.get((table_a, table_b), {})
        
        related_indices = []
        for idx_a in indices_a:
            row_a = df_a.iloc[idx_a]
            key_values = tuple(row_a[k] for k in keys)
            related = index_map.get(key_values, [])
            related_indices.append(related)
        
        return related_indices
    
    def get_batch(
        self,
        table_name: str,
        indices: List[int],
        codecs: Optional[Dict[str, any]] = None,
    ) -> Dict[str, TokenBatch]:
        """
        Get a batch of rows from a specific table, converted to TokenBatch format.
        
        Args:
            table_name: Name of the table
            indices: List of row indices to retrieve
            codecs: Optional codecs for tokenization (if None, uses self.codecs)
        
        Returns:
            Dict mapping column names to TokenBatch objects
        """
        if table_name not in self.tables:
            raise ValueError(f"Table '{table_name}' not found")
        
        df = self.tables[table_name]
        batch_df = df.iloc[indices]
        
        # Use provided codecs or fall back to instance codecs
        table_codecs = codecs or self.codecs.get(table_name, {})
        
        # Convert DataFrame to TokenBatch format
        column_batches = {}
        for col_name in batch_df.columns:
            col_values = batch_df[col_name].tolist()
            
            # Get codec for this column if available
            codec = table_codecs.get(col_name)
            
            if codec is not None and hasattr(codec, 'tokenize'):
                # Use codec to tokenize
                tokens = []
                for val in col_values:
                    try:
                        # codec.tokenize expects a single value, not a list
                        # It returns a Token object with proper value (tensor for strings, float for scalars, etc.)
                        token = codec.tokenize(val)
                        if token is None:
                            # Fallback: create unknown token based on codec type
                            if hasattr(codec, 'enc_dim'):
                                token = Token(value=torch.zeros(codec.enc_dim, dtype=torch.float32), status=TokenStatus.UNKNOWN)
                            else:
                                token = Token(value=0.0, status=TokenStatus.UNKNOWN)
                        tokens.append(token)
                    except Exception as e:
                        logger.debug(f"Error tokenizing {col_name}={val}: {e}")
                        # Fallback: create unknown token based on codec type
                        if codec is not None and hasattr(codec, 'enc_dim'):
                            tokens.append(Token(value=torch.zeros(codec.enc_dim, dtype=torch.float32), status=TokenStatus.UNKNOWN))
                        else:
                            tokens.append(Token(value=0.0, status=TokenStatus.UNKNOWN))
            else:
                # No codec - create basic tokens with float values
                # This should only happen for columns without codecs (shouldn't happen in normal flow)
                tokens = []
                for val in col_values:
                    if pd.notna(val):
                        try:
                            # Try to convert to float
                            float_val = float(val)
                            tokens.append(Token(value=float_val, status=TokenStatus.UNKNOWN))
                        except (ValueError, TypeError):
                            # Can't convert to float - use 0.0
                            tokens.append(Token(value=0.0, status=TokenStatus.UNKNOWN))
                    else:
                        tokens.append(Token(value=0.0, status=TokenStatus.NOT_PRESENT))
            
            column_batches[col_name] = TokenBatch(tokens)
        
        return column_batches
    
    def get_all_tables(self) -> List[str]:
        """Get list of all table names."""
        return list(self.tables.keys())
    
    def get_relationships(self) -> Dict[Tuple[str, str], str]:
        """Get all relationships as dict mapping (table_a, table_b) -> relationship_type."""
        return self.relationship_types.copy()
    
    def get_shared_keys(self) -> Dict[Tuple[str, str], List[str]]:
        """Get all shared keys as dict mapping (table_a, table_b) -> [key_columns]."""
        return self.shared_keys.copy()

