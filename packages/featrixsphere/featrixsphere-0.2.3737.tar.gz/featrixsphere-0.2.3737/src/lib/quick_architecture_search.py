"""
Quick Architecture Search

Runs a fast architecture search (25 epochs) to find optimal ES parameters
before full training. Uses random sampling + early stopping.
"""
import logging
import random
import asyncio
import time
from pathlib import Path
from typing import Dict, Any, List
from itertools import product
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


def analyze_dataset(df) -> Dict[str, List[int]]:
    """
    Analyze dataset to determine intelligent search space.
    
    Args:
        df: Training DataFrame
    
    Returns:
        Dict with parameter choices based on dataset size/complexity
    """
    n_rows = len(df)
    n_cols = len(df.columns) - 1  # Exclude target
    
    # Adaptive d_model based on columns
    if n_cols <= 10:
        d_model_choices = [64, 96]
    elif n_cols <= 30:
        d_model_choices = [96, 128]
    elif n_cols <= 60:
        d_model_choices = [128, 192]
    else:
        # Large datasets (60+ columns) - need more capacity
        d_model_choices = [192, 256]
    
    # Adaptive layers based on rows (more data = can go deeper)
    if n_rows < 1000:
        layer_choices = [2, 3, 4]  # Shallow - avoid overfitting
    elif n_rows < 10000:
        layer_choices = [3, 4, 6]
    else:
        layer_choices = [4, 6, 8, 10]  # Deep - can handle complexity
    
    # Heads: Keep 8-32 dims per head (d_model / n_heads)
    # For large datasets (60+ columns), allow up to 32 heads for complex interactions
    max_heads = 32 if n_cols >= 60 else 16
    head_options = [h for h in [2, 4, 8, 16, 32] if h <= max_heads]
    
    head_choices = []
    for d in d_model_choices:
        # Add heads that give reasonable dims/head
        for h in head_options:
            dims_per_head = d / h
            if 8 <= dims_per_head <= 32:  # Sweet spot
                if h not in head_choices:
                    head_choices.append(h)
    head_choices.sort()
    
    logger.info(f"📊 Dataset analysis:")
    logger.info(f"   {n_rows} rows, {n_cols} columns")
    logger.info(f"   Search space: d_model={d_model_choices}, layers={layer_choices}, heads={head_choices}")
    
    return {
        'd_model': d_model_choices,
        'n_transformer_layers': layer_choices,
        'n_attention_heads': head_choices,
    }


def sample_configs(search_space: Dict[str, List], n_samples: int = 20) -> List[Dict[str, int]]:
    """
    Sample configurations intelligently from search space.
    
    Strategy:
    - Always test extremes (min/max of each dimension)
    - Random sample the middle
    
    Args:
        search_space: Dict of parameter choices
        n_samples: Number of configs to sample
    
    Returns:
        List of config dicts
    """
    all_configs = list(product(
        search_space['d_model'],
        search_space['n_transformer_layers'],
        search_space['n_attention_heads']
    ))
    
    if len(all_configs) <= n_samples:
        # Small space - test everything
        configs = all_configs
    else:
        # Sample strategically
        configs_to_test = set()
        
        # Add corner cases (min/max combinations)
        configs_to_test.add(all_configs[0])   # Min everything
        configs_to_test.add(all_configs[-1])  # Max everything
        
        # Add mid-range
        mid_idx = len(all_configs) // 2
        if mid_idx < len(all_configs):
            configs_to_test.add(all_configs[mid_idx])
        
        # Random sample the rest
        remaining = n_samples - len(configs_to_test)
        if remaining > 0:
            available = [c for c in all_configs if c not in configs_to_test]
            if available:
                sampled = random.sample(available, min(remaining, len(available)))
                configs_to_test.update(sampled)
        
        configs = list(configs_to_test)
    
    # Convert to list of dicts
    config_dicts = [
        {
            'd_model': d,
            'n_transformer_layers': layers,
            'n_attention_heads': heads
        }
        for d, layers, heads in configs
    ]
    
    logger.info(f"🎲 Sampled {len(config_dicts)} configurations to test")
    
    return config_dicts


def run_quick_architecture_search(data_file: str, strings_cache: str, session_id: str,
                                   n_samples: int = 20, quick_epochs: int = 25, 
                                   suggested_configs: List[Dict[str, int]] = None,
                                   job_id: str = None) -> Dict[str, Any]:
    """
    Run quick architecture search on a dataset.
    
    Args:
        data_file: Path to SQLite database
        strings_cache: Path to strings cache
        session_id: Session ID (for loading data)
        n_samples: Number of configs to test (ignored if suggested_configs provided)
        quick_epochs: Epochs for quick search
        suggested_configs: Optional list of specific configs to test (from meta-learning)
                          Format: [{"d_model": 128, "n_transformer_layers": 6, "n_attention_heads": 8}, ...]
    
    Returns:
        Dict with optimal config
    """
    from featrix.neural.input_data_file import FeatrixInputDataFile
    from featrix.neural.input_data_set import FeatrixInputDataSet
    from featrix.neural.embedded_space import EmbeddingSpace
    from featrix.neural.single_predictor import FeatrixSinglePredictor
    from featrix.neural.simple_mlp import SimpleMLP
    from featrix.neural.model_config import SimpleMLPConfig
    import pandas as pd
    
    logger.info(f"📂 Loading dataset from: {data_file}")
    
    # Load data from SQLite database created by create_structured_data
    # NOTE: We use the data_file parameter (SQLite DB), NOT session.get('input_data') (original upload)
    if not data_file:
        from lib.session_manager import load_session
        
        # DEFENSIVE: Retry loading session to wait for sqlite_db to appear
        # This handles race condition where create_structured_data hasn't fully persisted yet
        max_retries = 6  # 6 retries = up to 30 seconds
        retry_sleep = 5  # 5 seconds between retries
        
        for attempt in range(max_retries):
            session = load_session(session_id)
            data_file = session.get('sqlite_db')
            
            if data_file:
                if attempt > 0:
                    logger.info(f"✅ Found sqlite_db after {attempt} retries ({attempt * retry_sleep}s)")
                break
            
            if attempt < max_retries - 1:
                logger.warning(f"⏳ sqlite_db not found in session yet, waiting {retry_sleep}s... (attempt {attempt + 1}/{max_retries})")
                time.sleep(retry_sleep)
            else:
                # Final attempt failed
                raise ValueError(f"No data_file provided and session {session_id} has no sqlite_db after {max_retries * retry_sleep}s")
    
    # Load from SQLite database
    input_file = FeatrixInputDataFile(str(data_file))
    df = input_file.df
    
    logger.info(f"✅ Loaded {len(df)} rows, {len(df.columns)} columns from SQLite database")
    
    # Use suggested configs from meta-learning if provided, otherwise sample adaptively
    if suggested_configs:
        logger.info(f"🎯 Using {len(suggested_configs)} suggested configs from meta-learning API")
        configs_to_test = suggested_configs
    else:
        # Analyze dataset to determine search space
        search_space = analyze_dataset(df)
        
        # Sample configurations
        configs_to_test = sample_configs(search_space, n_samples=n_samples)
        logger.info(f"🔀 Using adaptive sampling strategy")
    
    logger.info(f"🧪 Testing {len(configs_to_test)} configurations with {quick_epochs} epochs each")
    
    results = []
    total_configs = len(configs_to_test)
    best_config_so_far = None
    best_auc_so_far = -1.0
    
    # Helper function to update job progress in Redis
    def update_progress(config_num: int, config: Dict, auc: float = None, status: str = None, best_config: Dict = None, best_auc: float = None):
        """Update job progress in Redis if job_id is provided."""
        if not job_id:
            return
        
        try:
            from lib.job_manager import load_job, save_job
            job_data = load_job(job_id)
            if job_data:
                # Calculate progress percentage
                progress = config_num / total_configs if total_configs > 0 else 0
                job_data['progress'] = progress
                job_data['current_config'] = config_num
                job_data['total_configs'] = total_configs
                job_data['current_config_params'] = config
                if auc is not None:
                    job_data['current_auc'] = auc
                if status:
                    job_data['status_message'] = status
                
                # Store best config so far
                if best_config is not None and best_auc is not None:
                    job_data['best_config_so_far'] = best_config
                    job_data['best_auc_so_far'] = best_auc
                
                # Store results so far
                if 'config_results' not in job_data:
                    job_data['config_results'] = []
                # Keep only the last 20 results to avoid bloat
                if len(job_data['config_results']) >= 20:
                    job_data['config_results'] = job_data['config_results'][-19:]
                
                session_id_for_job = job_data.get('session_id') or session_id
                job_type = job_data.get('job_type') or 'pre_analysis_architecture'
                save_job(job_id, job_data, session_id_for_job, job_type)
        except Exception as e:
            # Don't fail search if progress update fails
            logger.debug(f"Failed to update job progress: {e}")
    
    for i, config in enumerate(configs_to_test, 1):
        logger.info(f"\n[{i}/{len(configs_to_test)}] Testing: {config}")
        
        # Update progress: starting config (include best so far)
        status_msg = f"Testing config {i}/{total_configs}: {config}"
        if best_config_so_far:
            status_msg += f" | Best so far: {best_config_so_far} (AUC: {best_auc_so_far:.4f})"
        update_progress(i, config, status=status_msg, best_config=best_config_so_far, best_auc=best_auc_so_far if best_config_so_far else None)
        
        try:
            # Create dataset
            dataset = FeatrixInputDataSet(df=df, ignore_cols=[], limit_rows=None)
            detected_types = {col: det.get_codec_name() for col, det in dataset._detectors.items()}
            dataset.encoderOverrides = detected_types
            train_data, val_data = dataset.split(fraction=0.2)
            
            # Train ES with this config
            es = EmbeddingSpace(
                train_data, val_data,
                d_model=config['d_model'],
                n_transformer_layers=config['n_transformer_layers'],
                n_attention_heads=config['n_attention_heads'],
                output_debug_label=f"quick_search_{i}",
                string_cache=strings_cache
            )
            es.train(batch_size=0, n_epochs=quick_epochs, movie_frame_interval=None)
            
            # Train quick SP to get validation AUC
            sp_config = SimpleMLPConfig(
                d_in=config['d_model'],
                d_out=2,  # Binary for now
                d_hidden=256,
                n_hidden_layers=2,  # Simple predictor for quick test
                dropout=0.1,
                normalize=False,
                residual=True,
                use_batch_norm=True
            )
            predictor = SimpleMLP(sp_config)
            fsp = FeatrixSinglePredictor(es, predictor)
            
            # Get target column (first non-excluded column or 'target')
            target_col = 'target' if 'target' in df.columns else df.columns[-1]
            
            fsp.prep_for_training(
                train_df=df,
                target_col_name=target_col,
                target_col_type='set'
            )
            
            # Train SP briefly
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            training_results = loop.run_until_complete(
                fsp.train(n_epochs=quick_epochs, batch_size=128, fine_tune=False, val_pos_label=None)
            )
            loop.close()
            
            # Extract final AUC
            if training_results and len(training_results) > 0:
                final_metrics = training_results[-1].get('metrics', {})
                auc = final_metrics.get('auc', 0)
            else:
                auc = 0
            
            logger.info(f"   Result: AUC={auc:.4f}")
            
            result = {
                **config,
                'auc': auc,
                'tested': True
            }
            results.append(result)
            
            # Update best config if this one is better
            if auc > best_auc_so_far:
                best_auc_so_far = auc
                best_config_so_far = config
                logger.info(f"   ⭐ New best config! AUC={auc:.4f}")
            
            # Update progress: config completed with result (include best so far)
            status_msg = f"Config {i}/{total_configs} completed: AUC={auc:.4f}"
            if best_config_so_far:
                status_msg += f" | Best: {best_config_so_far} (AUC: {best_auc_so_far:.4f})"
            update_progress(i, config, auc=auc, status=status_msg, best_config=best_config_so_far, best_auc=best_auc_so_far)
            
        except Exception as e:
            logger.exception(f"   ❌ Config failed: {type(e).__name__}: {e}")
            result = {
                **config,
                'auc': 0,
                'tested': False,
                'error': str(e)
            }
            results.append(result)
            
            # Update progress: config failed (still show best so far if we have one)
            status_msg = f"Config {i}/{total_configs} failed: {str(e)[:50]}"
            if best_config_so_far:
                status_msg += f" | Best so far: {best_config_so_far} (AUC: {best_auc_so_far:.4f})"
            update_progress(i, config, auc=0, status=status_msg, best_config=best_config_so_far, best_auc=best_auc_so_far if best_config_so_far else None)
    
    # Pick best config
    successful_results = [r for r in results if r.get('tested', False)]
    if not successful_results:
        logger.error("❌ No configs succeeded - using defaults")
        # Use more capable defaults for fallback
        optimal_config = {
            'd_model': 192,
            'n_transformer_layers': 6,
            'n_attention_heads': 16,
            'estimated_auc': 0,
            'used_default': True
        }
    else:
        best = max(successful_results, key=lambda x: x['auc'])
        optimal_config = {
            'd_model': best['d_model'],
            'n_transformer_layers': best['n_transformer_layers'],
            'n_attention_heads': best['n_attention_heads'],
            'estimated_auc': best['auc'],
            'configs_tested': len(results),
            'configs_succeeded': len(successful_results)
        }
    
    logger.info(f"🏆 Optimal config selected: {optimal_config}")
    
    # Save all tested configs and results to session for future reference
    try:
        from lib.session_manager import load_session, save_session
        session = load_session(session_id)
        
        # Store all tested configs and their results
        session['pre_analysis_results'] = {
            'all_tested_configs': results,
            'optimal_config': optimal_config,
            'total_configs_tested': len(results),
            'successful_configs': len(successful_results),
            'failed_configs': len([r for r in results if not r.get('tested', False)])
        }
        save_session(session_id, session, exist_ok=True)
        logger.info(f"💾 Saved all {len(results)} tested configs and results to session")
    except Exception as e:
        logger.warning(f"⚠️  Failed to save tested configs to session: {e}")
    
    # Final progress update: search complete
    if job_id:
        try:
            from lib.job_manager import load_job, save_job
            job_data = load_job(job_id)
            if job_data:
                job_data['progress'] = 1.0  # 100% complete
                auc_str = f"{optimal_config.get('estimated_auc', 0):.4f}" if optimal_config.get('estimated_auc') else "N/A"
                job_data['status_message'] = f"Search complete! Best config: d_model={optimal_config['d_model']}, layers={optimal_config['n_transformer_layers']}, heads={optimal_config['n_attention_heads']} (AUC: {auc_str})"
                job_data['optimal_config'] = optimal_config
                job_data['best_config_so_far'] = {
                    'd_model': optimal_config['d_model'],
                    'n_transformer_layers': optimal_config['n_transformer_layers'],
                    'n_attention_heads': optimal_config['n_attention_heads']
                }
                job_data['best_auc_so_far'] = optimal_config.get('estimated_auc', 0)
                session_id_for_job = job_data.get('session_id') or session_id
                job_type = job_data.get('job_type') or 'pre_analysis_architecture'
                save_job(job_id, job_data, session_id_for_job, job_type)
        except Exception as e:
            logger.debug(f"Failed to update final job progress: {e}")
    
    return optimal_config

