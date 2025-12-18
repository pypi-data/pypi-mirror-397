"""
Experiment Runner for QualSynth

This module provides the core experiment execution logic.
"""

# Set PyTorch environment variables BEFORE any imports
import os
os.environ['PYTORCH_MPS_METAL'] = '0'
os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'
os.environ['PYTORCH_MPS_HIGH_WATERMARK_RATIO'] = '0.0'
os.environ['CUDA_VISIBLE_DEVICES'] = ''
os.environ['MPS_DISABLE'] = '1'
os.environ['PYTORCH_MPS_ENABLED'] = '0'

import time
import json
import pickle
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, asdict
import pandas as pd
import numpy as np
from datetime import datetime

try:
    from ..utils.config_loader import ConfigLoader, DatasetConfig, MethodConfig
    from ..utils.experiment_logger import ExperimentLogger
    from ..data.splitting import load_split, encode_features, decode_features
    from ..evaluation.classifiers import ClassifierPipeline
    from ..evaluation.metrics import MetricsEvaluator
    from ..validation.universal_validator import UniversalValidator, ValidationResult
except ImportError:
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from src.qualsynth.utils.config_loader import ConfigLoader, DatasetConfig, MethodConfig
    from src.qualsynth.utils.experiment_logger import ExperimentLogger
    from src.qualsynth.data.splitting import load_split, encode_features, decode_features
    from src.qualsynth.evaluation.classifiers import ClassifierPipeline
    from src.qualsynth.evaluation.metrics import MetricsEvaluator
    from src.qualsynth.validation.universal_validator import UniversalValidator, ValidationResult


@dataclass
class ExperimentResult:
    """Result of a single experiment."""
    # Experiment metadata
    experiment_id: str
    dataset: str
    method: str
    seed: int
    timestamp: str
    
    # Execution info
    success: bool
    error: Optional[str] = None
    execution_time: float = 0.0
    
    # Generation info
    n_generated: int = 0
    generation_time: float = 0.0
    generation_cost: float = 0.0
    
    # Performance metrics (per classifier)
    performance_metrics: Dict[str, Dict[str, float]] = None
    
    # Fairness metrics (per classifier)
    fairness_metrics: Dict[str, Dict[str, float]] = None
    
    # Aggregated metrics (averaged across classifiers)
    avg_performance: Dict[str, float] = None
    avg_fairness: Dict[str, float] = None
    
    # Additional metadata
    metadata: Dict[str, Any] = None


class ExperimentRunner:
    """
    Runs individual experiments with specified configurations.
    
    Handles:
    - Data loading and splitting
    - Method execution (oversampling)
    - Classifier training
    - Metrics evaluation
    - Result saving
    """
    
    def __init__(
        self,
        config_dir: Optional[str] = None,
        output_dir: Optional[str] = None,
        verbose: bool = True,
        enable_universal_validation: bool = True  # Compute quality metrics (doesn't filter other methods)
    ):
        """
        Initialize experiment runner.
        
        Args:
            config_dir: Directory containing configuration files
            output_dir: Directory for saving results
            verbose: Whether to print progress messages
            enable_universal_validation: Compute validation pass rates as quality metric (doesn't filter other methods' samples)
        """
        self.config_loader = ConfigLoader(config_dir)
        
        if output_dir is None:
            project_root = Path(__file__).parent.parent.parent.parent
            output_dir = project_root / "results" / "experiments"
        
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.verbose = verbose
        self.enable_universal_validation = enable_universal_validation
        
        # Initialize universal validator for QUALITY METRICS only
        # This computes validation pass rates to show Qualsynth generates higher-quality samples
        # But does NOT filter other methods' samples - they use their native pipelines
        self.universal_validator = UniversalValidator(
            duplicate_threshold=0.85,
            quality_threshold=0.5,
            diversity_weight=0.15,
            fairness_weight=0.70,
            performance_weight=0.15,
            max_samples=None,
            verbose=self.verbose,
            use_adaptive_threshold=True,
            statistical_std_threshold=3.5,
            enable_semantic_dedup=False
        )
        if self.verbose and self.enable_universal_validation:
            print("✅ Universal validation enabled")
    
    def run_experiment(
        self,
        dataset_name: str,
        method_name: str,
        seed: int,
        save_results: bool = True,
        max_iterations_override: Optional[int] = None,
        model_name_override: Optional[str] = None,
        batch_size_override: Optional[int] = None
    ) -> ExperimentResult:
        """
        Run a single experiment.
        
        Args:
            dataset_name: Name of the dataset
            method_name: Name of the method
            seed: Random seed
            save_results: Whether to save results to disk
            max_iterations_override: Override max_iterations for QualSynth methods
            model_name_override: Override LLM model name
            batch_size_override: Override batch_size for QualSynth methods
        
        Returns:
            ExperimentResult object
        """
        experiment_id = f"{dataset_name}_{method_name}_seed{seed}"
        
        # Store overrides for use in _apply_* methods
        self._max_iterations_override = max_iterations_override
        self._model_name_override = model_name_override
        self._batch_size_override = batch_size_override
        
        # Initialize logger
        logger = ExperimentLogger(experiment_id)
        logger.start_experiment(dataset_name, method_name, seed)
        
        start_time = time.time()
        
        try:
            # Load configurations
            logger.start_step("load_config", "Loading dataset and method configurations")
            dataset_config = self.config_loader.load_dataset_config(dataset_name)
            method_config = self.config_loader.load_method_config(method_name)
            logger.complete_step("load_config")
            
            # Load RAW data - ALL methods use RAW, encoding happens at training time
            # This ensures FAIR COMPARISON: same scaler/encoder for all methods
            logger.start_step("load_data", f"Loading {dataset_name} dataset")
            logger.update_step(f"Loading split with seed={seed}")
            
            split_data = load_split(
                dataset_name, 
                seed=seed, 
                return_raw=True,  # ALL methods use RAW data
                include_sensitive_indicators=True,
                dataset_config=dataset_config
            )
            
            X_train = split_data['X_train']  # RAW
            y_train = split_data['y_train']
            X_test = split_data['X_test']    # RAW
            y_test = split_data['y_test']
            
            # Store preprocessor for encoding ALL generated samples before training
            preprocessor = split_data.get('preprocessor', None)
            
            # Load protected group indicators for fairness evaluation
            sensitive_train = split_data.get('sensitive_train', None)
            sensitive_test = split_data.get('sensitive_test', None)
            
            logger.update_step(f"Train: {len(X_train)} samples (RAW), Test: {len(X_test)} samples")
            logger.complete_step("load_data", {
                'n_train': len(X_train),
                'n_test': len(X_test)
            })
            
            # Apply oversampling method
            logger.start_step("apply_method", f"Applying {method_name}")
            logger.update_step(f"Method type: {method_config.type}")
            logger.update_step(f"Starting generation...")
            
            gen_start = time.time()
            
            from src.qualsynth.data.splitting import encode_features, decode_features
            
            # Determine if method needs encoded input (SMOTE, CTGAN need numerical)
            # LLM-based methods (qualsynth) work with RAW data
            is_llm_method = method_name.lower().startswith('qualsynth')
            
            if is_llm_method:
                # LLM methods: use RAW data, generate RAW samples
                X_input = X_train
                logger.update_step(f"Using RAW data for LLM-based method")
            else:
                # Traditional methods (SMOTE, CTGAN, Random): need ENCODED data
                if preprocessor is not None:
                    X_input = encode_features(X_train, preprocessor)
                    logger.update_step(f"Encoded input for {method_name} (requires numerical data)")
                else:
                    X_input = X_train
            
            X_resampled_method, y_resampled, gen_metadata = self._apply_method(
                method_name,
                method_config,
                X_input,
                y_train,
                dataset_config,
                seed,
                logger,
                dataset_name=dataset_name,
                preprocessor=preprocessor
            )
            gen_time = time.time() - gen_start
            
            X_resampled = X_resampled_method
            if preprocessor is not None:
                X_resampled_raw = decode_features(X_resampled_method, preprocessor)
                logger.update_step(f"Decoded {len(X_resampled_raw)} samples for CSV saving")
            else:
                X_resampled_raw = X_resampled_method
            
            # Get n_generated from metadata if available (for QualSynth), otherwise calculate
            n_original = len(X_train)
            n_generated = gen_metadata.get('n_generated', len(X_resampled) - n_original)
            
            # Store resampled size in metadata for verification
            gen_metadata['X_resampled_size'] = len(X_resampled)
            gen_metadata['X_train_size'] = n_original
            gen_metadata['calculated_n_generated'] = len(X_resampled) - n_original
            
            result_data = {
                'n_generated': n_generated,
                'generation_time': gen_time
            }
            if 'cost' in gen_metadata:
                result_data['cost'] = gen_metadata['cost']
                logger.update_step(f"Generated {n_generated} samples in {gen_time:.2f}s (cost: ${gen_metadata['cost']:.4f})")
            else:
                logger.update_step(f"Generated {n_generated} samples in {gen_time:.2f}s")
            
            logger.complete_step("apply_method", result_data)
            
            # Save generated samples to CSV (for non-QualSynth methods only)
            # QualSynth saves its own CSVs during iterations via _save_iteration_csv()
            # to preserve accumulated validated samples across all iterations
            if save_results and not method_name.startswith('qualsynth'):
                # Save VALIDATED samples (what training actually uses)
                # X_resampled_raw contains original + validated samples after _apply_method
                self._save_generated_samples_csv(
                    X_train=X_train,  # RAW for human-readable CSV
                    X_resampled=X_resampled_raw,  # Original + validated samples
                    y_resampled=y_resampled,
                    dataset_name=dataset_name,
                    method_name=method_name,
                    seed=seed,
                    logger=logger
                )
            
            # Encode test data for evaluation (same encoder as training)
            if preprocessor is not None:
                X_test_encoded = encode_features(X_test, preprocessor)
                # For fairness eval, use encoded original train (X_input is already encoded)
                X_train_encoded = X_input
            else:
                X_test_encoded = X_test
                X_train_encoded = X_train
            
            # Train classifiers and evaluate (using ENCODED data)
            logger.start_step("evaluate", "Training classifiers and computing metrics")
            logger.update_step("Training 3 classifiers (RF, XGBoost, LR)")
            
            # Validate y_resampled before evaluation
            valid_labels = {0, 1}
            invalid_mask = ~y_resampled.isin(valid_labels)
            if invalid_mask.any():
                n_invalid = invalid_mask.sum()
                invalid_vals = y_resampled[invalid_mask].unique().tolist()
                logger.update_step(f"⚠️  Fixing {n_invalid} invalid labels in y_resampled: {invalid_vals}")
                # Get the actual minority class from valid labels
                valid_y = y_resampled[~invalid_mask]
                minority_class = valid_y.value_counts().idxmin() if len(valid_y) > 0 else 1
                y_resampled = y_resampled.copy()
                y_resampled.loc[invalid_mask] = minority_class
            
            # Also validate y_test
            invalid_test_mask = ~y_test.isin(valid_labels)
            if invalid_test_mask.any():
                n_invalid = invalid_test_mask.sum()
                logger.update_step(f"⚠️  Fixing {n_invalid} invalid labels in y_test")
                y_test = y_test.copy()
                y_test.loc[invalid_test_mask] = 0  # Default to majority class
            
            performance_metrics, fairness_metrics = self._evaluate(
                X_resampled,  # Encoded training data (original + generated)
                y_resampled,
                X_test_encoded,  # Encoded test data
                y_test,
                X_train_encoded,  # For fairness evaluation
                dataset_config,
                seed,
                logger,
                sensitive_test=sensitive_test  # Protected group indicators
            )
            
            # Aggregate metrics
            avg_performance = self._aggregate_metrics(performance_metrics)
            avg_fairness = self._aggregate_metrics(fairness_metrics)
            
            logger.update_step("Computing aggregated metrics")
            logger.log_metrics({
                'f1': avg_performance.get('f1', 0),
                'roc_auc': avg_performance.get('roc_auc', 0),
                'recall': avg_performance.get('recall', 0)
            }, prefix="Performance ")
            logger.log_metrics({
                k: v for k, v in list(avg_fairness.items())[:3]
            }, prefix="Fairness ")
            logger.complete_step("evaluate")
            
            # Create result object
            result = ExperimentResult(
                experiment_id=experiment_id,
                dataset=dataset_name,
                method=method_name,
                seed=seed,
                timestamp=datetime.now().isoformat(),
                success=True,
                execution_time=time.time() - start_time,
                n_generated=n_generated,
                generation_time=gen_time,
                generation_cost=gen_metadata.get('cost', 0.0),
                performance_metrics=performance_metrics,
                fairness_metrics=fairness_metrics,
                avg_performance=avg_performance,
                avg_fairness=avg_fairness,
                metadata=gen_metadata
            )
            
            # Save results
            if save_results:
                logger.start_step("save_results", "Saving experiment results")
                self._save_result(result)
                logger.complete_step("save_results")
            
            logger.complete_experiment(True, {
                'execution_time': result.execution_time,
                'n_generated': result.n_generated,
                'avg_f1': result.avg_performance.get('f1', 0),
                'avg_dpd': result.avg_fairness.get('demographic_parity_difference', 0)
            })
            
            return result
        
        except Exception as e:
            import traceback
            logger.error(f"Experiment failed with error: {str(e)}")
            logger.error(f"Full traceback:\n{traceback.format_exc()}")
            logger.fail_step("experiment", str(e))
            logger.complete_experiment(False)
            
            result = ExperimentResult(
                experiment_id=experiment_id,
                dataset=dataset_name,
                method=method_name,
                seed=seed,
                timestamp=datetime.now().isoformat(),
                success=False,
                error=str(e),
                execution_time=time.time() - start_time
            )
            
            if save_results:
                self._save_result(result)
            
            return result
    
    def _apply_method(
        self,
        method_name: str,
        method_config: MethodConfig,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        dataset_config: DatasetConfig,
        seed: int,
        logger: Optional[ExperimentLogger] = None,
        dataset_name: Optional[str] = None,
        preprocessor = None  # For encoding Qualsynth output
    ) -> tuple:
        """
        Apply oversampling method.
        
        Returns:
            (X_resampled, y_resampled, metadata)
        """
        # Set random seed in hyperparameters
        hyperparams = method_config.hyperparameters.copy()
        hyperparams['random_state'] = seed
        
        metadata = {}
        
        # Route to appropriate method
        if method_name == 'smote':
            X_res, y_res, metadata = self._apply_smote(X_train, y_train, hyperparams)
        
        elif method_name == 'ctgan':
            X_res, y_res, metadata = self._apply_ctgan(X_train, y_train, hyperparams)
        
        elif method_name == 'tabfairgdt':
            X_res, y_res, metadata = self._apply_tabfairgdt(
                X_train, y_train, dataset_config, hyperparams
            )
        
        elif method_name.startswith('qualsynth'):
            # QualSynth (all variants)
            X_res, y_res, metadata = self._apply_qualsynth(
                X_train, y_train, dataset_config, hyperparams, seed=seed, method_name=method_name,
                preprocessor=preprocessor
            )
        
        else:
            raise ValueError(f"Unknown method: {method_name}")
        
        if not method_name.startswith('qualsynth'):
            # Extract generated samples (everything after original training data)
            n_train = len(X_train)
            X_generated = X_res.iloc[n_train:].copy()
            y_generated = y_res.iloc[n_train:].copy()
            
            # Get sensitive features if available
            sensitive_features = None
            if hasattr(dataset_config, 'sensitive_attributes') and dataset_config.sensitive_attributes:
                try:
                    from ..data.splitting import load_split
                    split_data = load_split(dataset_config.name, seed=seed, return_raw=True)
                    if 'sensitive_features_train_raw' in split_data:
                        sensitive_features = split_data['sensitive_features_train_raw']
                except:
                    pass
            
            # Handle NaN values in X_train for validation (same as SMOTE/CTGAN do internally)
            X_train_clean = X_train.copy()
            for col in X_train_clean.columns:
                if X_train_clean[col].isna().any():
                    median_val = X_train_clean[col].median()
                    if pd.isna(median_val):
                        median_val = 0
                    X_train_clean[col] = X_train_clean[col].fillna(median_val)
            X_train_clean = X_train_clean.fillna(0)  # Final safety
            
            X_validated, y_validated, metadata = self._apply_universal_validation(
                X_generated=X_generated,
                y_generated=y_generated,
                X_train=X_train_clean,  # Use cleaned data for validation
                y_train=y_train,
                sensitive_features=sensitive_features,
                method_name=method_name,
                metadata=metadata
            )
            
            # Save validated samples CSV (for quality analysis)
            self._save_validated_samples_csv(
                X_generated=X_generated,
                y_generated=y_generated,
                X_validated=X_validated,
                y_validated=y_validated,
                dataset_name=dataset_name,
                method_name=method_name,
                seed=seed
            )
            
            if self.verbose:
                n_generated = len(X_generated)
                n_validated = len(X_validated)
                pass_rate = n_validated / n_generated * 100 if n_generated > 0 else 0
                print(f"   📊 Quality metric: {n_validated}/{n_generated} ({pass_rate:.1f}%) pass validation")
                print(f"   ✅ Using ALL {n_generated} samples for training (fair comparison)")
        else:
            pass  # QualSynth saves CSVs during iterations
        
        return X_res, y_res, metadata
    
    def _apply_universal_validation(
        self,
        X_generated: pd.DataFrame,
        y_generated: pd.Series,
        X_train: pd.DataFrame,
        y_train: pd.Series,
        sensitive_features: Optional[pd.DataFrame],
        method_name: str,
        metadata: Dict[str, Any]
    ) -> Tuple[pd.DataFrame, pd.Series, Dict[str, Any]]:
        """
        Apply universal validation pipeline to generated samples.
        
        This is ALWAYS applied for non-QualSynth methods to ensure fair comparison.
        
        Args:
            X_generated: Generated samples
            y_generated: Generated labels
            X_train: Original training data
            y_train: Original training labels
            sensitive_features: Sensitive features
            method_name: Name of the generation method
            metadata: Existing metadata dict
        
        Returns:
            Tuple of (X_validated, y_validated, updated_metadata)
        """
        # Apply validation (always enabled for fair validated vs validated comparison)
        result = self.universal_validator.validate_and_select(
            X_generated=X_generated,
            y_generated=y_generated,
            X_train=X_train,
            y_train=y_train,
            sensitive_features=sensitive_features,
            method_name=method_name
        )
        
        # Update metadata with validation statistics
        metadata['validation'] = {
            'n_original': result.n_original,
            'n_after_dedup': result.n_after_dedup,
            'n_after_quality': result.n_after_quality,
            'n_after_selection': result.n_after_selection,
            'duplicate_ratio': result.duplicate_ratio,
            'quality_pass_rate': result.quality_pass_rate,
            'selection_rate': result.selection_rate,
            'overall_pass_rate': result.overall_pass_rate
        }
        
        return result.X_validated, result.y_validated, metadata
    
    def _apply_smote(self, X_train, y_train, hyperparams):
        """Apply SMOTE."""
        from imblearn.over_sampling import SMOTE
        
        # Handle NaN values by imputing with median
        X_train_clean = X_train.copy()
        for col in X_train_clean.columns:
            if X_train_clean[col].isna().any():
                median_val = X_train_clean[col].median()
                if pd.isna(median_val):
                    median_val = 0
                X_train_clean[col] = X_train_clean[col].fillna(median_val)
        X_train_clean = X_train_clean.fillna(0)  # Final safety
        
        smote = SMOTE(
            k_neighbors=hyperparams.get('k_neighbors', 5),
            sampling_strategy=hyperparams.get('sampling_strategy', 'auto'),
            random_state=hyperparams['random_state']
        )
        
        X_res, y_res = smote.fit_resample(X_train_clean, y_train)
        
        # Return metadata for consistency with other methods
        metadata = {
            'n_generated': len(X_res) - len(X_train),
            'sampling_strategy': hyperparams.get('sampling_strategy', 'auto'),
            'k_neighbors': hyperparams.get('k_neighbors', 5)
        }
        
        return X_res, y_res, metadata
    
    def _apply_ctgan(self, X_train, y_train, hyperparams):
        """Apply CTGAN."""
        from src.qualsynth.baselines.ctgan_baseline import CTGANBaseline
        
        # Handle NaN values by imputing with median
        X_train_clean = X_train.copy()
        for col in X_train_clean.columns:
            if X_train_clean[col].isna().any():
                median_val = X_train_clean[col].median()
                if pd.isna(median_val):
                    median_val = 0
                X_train_clean[col] = X_train_clean[col].fillna(median_val)
        X_train_clean = X_train_clean.fillna(0)  # Final safety
        
        ctgan = CTGANBaseline(
            epochs=hyperparams.get('epochs', 300),
            batch_size=hyperparams.get('batch_size', 500),
            random_state=hyperparams['random_state']
        )
        
        X_res, y_res = ctgan.fit_resample(X_train_clean, y_train)
        metadata = {'cost': 0.0}  # No API cost
        
        return X_res, y_res, metadata
    
    def _apply_tabfairgdt(self, X_train, y_train, dataset_config, hyperparams):
        """Apply TabFairGDT."""
        from src.qualsynth.baselines.tabfairgdt import TabFairGDT
        
        # Handle NaN values by imputing with median
        X_train_clean = X_train.copy()
        for col in X_train_clean.columns:
            if X_train_clean[col].isna().any():
                median_val = X_train_clean[col].median()
                if pd.isna(median_val):
                    median_val = 0
                X_train_clean[col] = X_train_clean[col].fillna(median_val)
        X_train_clean = X_train_clean.fillna(0)  # Final safety
        
        # Get sensitive features (handle empty list)
        if dataset_config.sensitive_attributes and len(dataset_config.sensitive_attributes) > 0:
            if isinstance(dataset_config.sensitive_attributes[0], dict):
                sensitive_cols = [attr['name'] for attr in dataset_config.sensitive_attributes]
            else:
                sensitive_cols = dataset_config.sensitive_attributes
            sensitive_features = X_train_clean[sensitive_cols].copy()
        else:
            # No sensitive attributes - use first column as placeholder
            sensitive_cols = [X_train_clean.columns[0]]
            sensitive_features = X_train_clean[sensitive_cols].copy()
        
        tabfair = TabFairGDT(
            n_estimators=hyperparams.get('n_estimators', 100),
            max_depth=hyperparams.get('max_depth', 5),
            fairness_weight=hyperparams.get('fairness_weight', 0.5),
            random_state=hyperparams['random_state']
        )
        
        # TabFairGDT uses generate() method, not fit_resample()
        # Determine minority class and target samples
        class_counts = y_train.value_counts()
        minority_class = int(class_counts.idxmin())  # Ensure int type
        majority_count = class_counts.max()
        minority_count = class_counts.min()
        n_samples_needed = majority_count - minority_count
        
        # Ensure minority_class is valid (0 or 1)
        valid_classes = {0, 1}  # Force binary classification
        if minority_class not in valid_classes:
            minority_class = 1  # Default to 1 for binary classification
        
        result = tabfair.generate(
            X_train=X_train_clean,
            y_train=y_train,
            n_samples=n_samples_needed,
            sensitive_features=sensitive_features,
            target_class=minority_class
        )
        
        # Combine original + generated (use cleaned data)
        X_res = pd.concat([X_train_clean, result.samples], ignore_index=True)
        
        # Create labels for generated samples - ensure they are valid (0 or 1)
        gen_labels = pd.Series([minority_class] * len(result.samples), dtype=int)
        
        y_res = pd.concat([y_train.astype(int), gen_labels], ignore_index=True)
        
        y_res = y_res.astype(int)
        y_res = y_res.clip(lower=0, upper=1)
        y_res = y_res.apply(lambda x: minority_class if x not in valid_classes else x)
        
        if self.verbose:
            unique_labels = y_res.unique()
            if not all(l in valid_classes for l in unique_labels):
                print(f"   ⚠️  Warning: Found unexpected labels: {unique_labels}")
        
        # Return metadata for consistency with other methods
        metadata = {
            'n_generated': len(result.samples),
            'minority_class': minority_class,
            'n_samples_needed': n_samples_needed
        }
        
        return X_res, y_res, metadata
    
    def _apply_qualsynth(self, X_train, y_train, dataset_config, hyperparams, seed=None, method_name="qualsynth", preprocessor=None):
        """Apply QualSynth."""
        from src.qualsynth.core.iterative_workflow import IterativeRefinementWorkflow, WorkflowConfig
        
        # Get sensitive features (handle empty list)
        if dataset_config.sensitive_attributes and len(dataset_config.sensitive_attributes) > 0:
            if isinstance(dataset_config.sensitive_attributes[0], dict):
                sensitive_cols = [attr['name'] for attr in dataset_config.sensitive_attributes]
            else:
                sensitive_cols = dataset_config.sensitive_attributes
            sensitive_features = X_train[sensitive_cols].copy()
        else:
            # No sensitive attributes - create empty DataFrame
            sensitive_cols = []
            sensitive_features = None
        
        # Override model name (priority: CLI > env var > config)
        model_name = hyperparams.get('model_name', 'gemma3-m4')
        
        # Check for command-line override first
        if hasattr(self, '_model_name_override') and self._model_name_override is not None:
            model_name = self._model_name_override
            if self.verbose:
                print(f"   → Using CLI override model: {model_name}")
        # Then check environment variables
        elif os.getenv('OLLAMA_MODEL'):
            model_name = os.getenv('OLLAMA_MODEL')
            if self.verbose:
                print(f"   → Using Ollama model: {model_name}")
        elif os.getenv('LMSTUDIO_MODEL'):
            model_name = os.getenv('LMSTUDIO_MODEL')
            if self.verbose:
                print(f"   → Using LM Studio model: {model_name}")
        
        # Calculate number of samples needed (same as other methods)
        class_counts = y_train.value_counts()
        minority_class = class_counts.idxmin()
        majority_count = class_counts.max()
        minority_count = class_counts.min()
        n_samples_needed = majority_count - minority_count
        
        # Create workflow config
        max_iterations = hyperparams.get('max_iterations', 8)
        if hasattr(self, '_max_iterations_override') and self._max_iterations_override is not None:
            max_iterations = self._max_iterations_override
            if self.verbose:
                if max_iterations == 0:
                    print(f"   ⚙️  Target-based looping: No iteration limit (loop until target samples reached)")
                else:
                    print(f"   ⚙️  Overriding max_iterations: {hyperparams.get('max_iterations', 8)} → {max_iterations}")
        elif max_iterations is None:
            # Auto-predict optimal iterations using AdaptiveIterationPredictor
            try:
                from src.qualsynth.utils.adaptive_iteration_predictor import AdaptiveIterationPredictor
                
                if self.verbose:
                    print(f"   🔮 Auto-predicting optimal iterations...")
                
                predictor = AdaptiveIterationPredictor(
                    target_samples=None,  # Auto-calculate 1:1 balance
                    max_time_hours=2.0,
                    max_samples=10000,  # High cap to not limit 1:1 balance
                    batch_size=hyperparams.get('batch_size', 100)
                )
                
                result = predictor.predict(X_train, y_train)
                max_iterations = result.predicted_iterations
                
                if self.verbose:
                    print(f"   ✅ Predicted iterations: {max_iterations}")
                    print(f"      → Expected samples: ~{result.expected_samples}")
                    print(f"      → Estimated time: ~{result.estimated_time_minutes:.1f} minutes")
            except Exception as e:
                # Fallback to default if predictor fails
                max_iterations = 12
                if self.verbose:
                    print(f"   ⚠️  Predictor failed ({e}), using default: {max_iterations}")
        
        # Apply batch_size override if provided
        batch_size = hyperparams.get('batch_size', 20)
        if hasattr(self, '_batch_size_override') and self._batch_size_override is not None:
            batch_size = self._batch_size_override
            if self.verbose:
                print(f"   ⚙️  Overriding batch_size: {hyperparams.get('batch_size', 20)} → {batch_size}")
        
        config = WorkflowConfig(
            model_name=model_name,
            temperature=hyperparams.get('temperature', 0.7),
            target_samples=n_samples_needed,  # Use calculated samples needed, not fixed 200
            batch_size=batch_size,
            max_iterations=max_iterations,
            min_iterations=hyperparams.get('min_iterations', 3),
            stall_iterations=hyperparams.get('stall_iterations', 10),  # Stop if no progress for N iterations
            fairness_threshold=hyperparams.get('fairness_threshold', 0.05),
            fairness_weight=hyperparams.get('fairness_weight', 0.7),
            counterfactual_ratio=hyperparams.get('counterfactual_ratio', 0.8),
            improvement_threshold=hyperparams.get('improvement_threshold', 0.005),
            duplicate_threshold=hyperparams.get('duplicate_threshold', 0.85),
            quality_threshold=hyperparams.get('quality_threshold', 0.5),
            diversity_weight=hyperparams.get('diversity_weight', 0.15),
            performance_weight=hyperparams.get('performance_weight', 0.15),
            enable_diversity_prompting=hyperparams.get('enable_diversity_prompting', True),
            diversity_prompt_strength=hyperparams.get('diversity_prompt_strength', 'high'),
            enable_sota_dedup=hyperparams.get('enable_sota_dedup', False),
            sota_diversity_threshold=hyperparams.get('sota_diversity_threshold', 0.05),
            top_p=hyperparams.get('top_p', 0.95),
            presence_penalty=hyperparams.get('presence_penalty', 0.6),
            frequency_penalty=hyperparams.get('frequency_penalty', 0.6),
            # Adaptive validation
            enable_adaptive_validation=hyperparams.get('enable_adaptive_validation', True),
            adaptive_std_threshold=hyperparams.get('adaptive_std_threshold', 3.5),
            # Statistical validation control
            enable_statistical_validation=hyperparams.get('enable_statistical_validation', True)
        )
        
        workflow = IterativeRefinementWorkflow(
            config=config, 
            method_name=method_name, 
            seed=seed, 
            preprocessor=preprocessor,
            output_dir=str(self.output_dir)  # Pass output directory for CSV logs
        )
        
        # Update universal validator with config values
        if self.universal_validator is not None:
            self.universal_validator.enable_semantic_dedup = hyperparams.get('enable_semantic_dedup', False)
        
        # Run workflow
        result = workflow.run(
            X_train=X_train,
            y_train=y_train,
            sensitive_features=sensitive_features,
            dataset_name=dataset_config.name
        )
        
        # Combine original + generated
        n_generated = 0
        # Check if samples were actually generated (even if result.success is False)
        if hasattr(result, 'X_generated') and result.X_generated is not None and len(result.X_generated) > 0:
            X_gen = result.X_generated.copy()
            
            # Encode X_train to match (it's RAW)
            if preprocessor is not None:
                X_train_encoded = encode_features(X_train, preprocessor)
            else:
                X_train_encoded = X_train
            
            # Check if generated data is RAW or ENCODED
            needs_encoding = False
            if preprocessor is not None and hasattr(preprocessor, 'label_encoders'):
                for col in preprocessor.label_encoders.keys():
                    if col in X_gen.columns:
                        if X_gen[col].dtype == 'object' or not pd.api.types.is_numeric_dtype(X_gen[col]):
                            needs_encoding = True
                            break
            
            if needs_encoding:
                if self.verbose:
                    print(f"   🔄 Encoding generated samples (loaded from RAW CSV)")
                X_gen_aligned = encode_features(X_gen, preprocessor)
            else:
                X_gen_aligned = X_gen
            
            # Remove any columns in generated data that aren't in training data
            extra_cols = set(X_gen_aligned.columns) - set(X_train_encoded.columns)
            if extra_cols:
                if self.verbose:
                    print(f"   ⚠️  Removing {len(extra_cols)} extra columns from generated data: {list(extra_cols)[:5]}")
                X_gen_aligned = X_gen_aligned.drop(columns=list(extra_cols))
            
            # Add missing columns (fill with encoded defaults)
            missing_cols = set(X_train_encoded.columns) - set(X_gen_aligned.columns)
            if missing_cols:
                if self.verbose:
                    print(f"   ⚠️  Adding {len(missing_cols)} missing columns to generated data: {list(missing_cols)[:5]}")
                for col in missing_cols:
                    # Use median (data is encoded/numerical)
                    X_gen_aligned[col] = X_train_encoded[col].median()
            
            # Ensure column order matches training data
            X_gen_aligned = X_gen_aligned[X_train_encoded.columns]
            
            # Count generated samples
            n_generated = len(X_gen_aligned)
            
            # Concatenate ENCODED data (both X_train_encoded and X_gen_aligned are encoded)
            X_res = pd.concat([X_train_encoded, X_gen_aligned], ignore_index=True)
            y_res = pd.concat([y_train, result.y_generated], ignore_index=True)
        else:
            # No samples generated - encode X_train for consistency
            n_generated = 0
            if preprocessor is not None:
                X_res = encode_features(X_train, preprocessor)
            else:
                X_res = X_train
            y_res = y_train
        
        metadata = {
            'cost': getattr(result, 'total_cost', 0.0),
            'iterations': getattr(result, 'total_iterations', 0),
            'validation_rate': getattr(result, 'total_validated', 0) / max(getattr(result, 'total_generated', 1), 1),
            'n_generated': n_generated  # Number of generated samples
        }
        
        return X_res, y_res, metadata
    
    def _evaluate(
        self,
        X_train,
        y_train,
        X_test,
        y_test,
        X_train_original,
        dataset_config,
        seed,
        logger: Optional[ExperimentLogger] = None,
        sensitive_test: Optional[pd.DataFrame] = None
    ):
        """
        Evaluate with multiple classifiers.
        
        Args:
            sensitive_test: Optional DataFrame with binary protected group indicators
                           (e.g., age_protected, marital_protected)
        
        Returns:
            (performance_metrics, fairness_metrics)
        """
        # Use provided sensitive indicators if available, otherwise fall back to old method
        if sensitive_test is None or len(sensitive_test.columns) == 0:
            # Check if dataset has sensitive attributes
            if dataset_config.sensitive_attributes and len(dataset_config.sensitive_attributes) > 0:
                # Fallback: Get sensitive features from X_test (old method - has issues with normalized features)
                if isinstance(dataset_config.sensitive_attributes[0], dict):
                    sensitive_cols = [attr['name'] for attr in dataset_config.sensitive_attributes]
                else:
                    sensitive_cols = dataset_config.sensitive_attributes
                
                # Filter to only columns that exist in test data
                sensitive_cols = [col for col in sensitive_cols if col in X_test.columns]
                if not sensitive_cols:
                    # Fallback: use first column if no sensitive columns found
                    sensitive_cols = [X_test.columns[0]]
                    if logger:
                        logger.update_step(f"⚠️  No sensitive columns found, using first column: {sensitive_cols[0]}")
                
                sensitive_test = X_test[sensitive_cols].copy()
                if logger:
                    logger.update_step(f"⚠️  Using normalized features for fairness (may cause issues)")
            else:
                # No sensitive attributes defined - skip fairness evaluation
                sensitive_test = None
                if logger:
                    logger.update_step(f"ℹ️  No sensitive attributes defined - skipping fairness evaluation")
        else:
            if logger:
                logger.update_step(f"✅ Using binary protected group indicators: {list(sensitive_test.columns)}")
        
        # Initialize evaluators
        clf_pipeline = ClassifierPipeline(random_state=seed)
        metrics_eval = MetricsEvaluator()
        
        # Import fairness evaluator
        try:
            from ..evaluation.fairness import FairnessEvaluator
        except ImportError:
            from src.qualsynth.evaluation.fairness import FairnessEvaluator
        
        fairness_eval = FairnessEvaluator()
        
        # Get default classifiers
        clf_configs = clf_pipeline.get_default_classifiers()
        
        performance_metrics = {}
        fairness_metrics = {}
        
        # Clean data: replace empty strings and invalid values with NaN, then fill
        # This handles cases where LLM generates empty strings or invalid values
        X_train_clean = X_train.copy()
        X_test_clean = X_test.copy()
        
        # Ensure both datasets have the same columns
        common_cols = set(X_train_clean.columns) & set(X_test_clean.columns)
        if len(common_cols) != len(X_train_clean.columns) or len(common_cols) != len(X_test_clean.columns):
            # Align columns
            missing_in_test = set(X_train_clean.columns) - set(X_test_clean.columns)
            missing_in_train = set(X_test_clean.columns) - set(X_train_clean.columns)
            if missing_in_test:
                if logger:
                    logger.update_step(f"Adding {len(missing_in_test)} missing columns to test set")
                for col in missing_in_test:
                    X_test_clean[col] = X_train_clean[col].median() if pd.api.types.is_numeric_dtype(X_train_clean[col]) else X_train_clean[col].mode()[0] if len(X_train_clean[col].mode()) > 0 else 0
            if missing_in_train:
                if logger:
                    logger.update_step(f"Removing {len(missing_in_train)} extra columns from test set")
                X_test_clean = X_test_clean.drop(columns=list(missing_in_train))
            # Use only common columns
            X_train_clean = X_train_clean[list(common_cols)]
            X_test_clean = X_test_clean[list(common_cols)]
        
        for col in X_train_clean.columns:
            if col not in X_test_clean.columns:
                continue  # Skip if column doesn't exist in test set
            # Replace empty strings and common invalid values with NaN
            X_train_clean[col] = X_train_clean[col].replace(['', ' ', 'nan', 'None', 'null', 'NaN'], np.nan)
            X_test_clean[col] = X_test_clean[col].replace(['', ' ', 'nan', 'None', 'null', 'NaN'], np.nan)
            
            # For object columns that should be numeric, try to convert
            if X_train_clean[col].dtype == 'object':
                # Check if column can be converted to numeric
                try:
                    # Try converting a sample to see if it's numeric
                    sample_val = X_train_clean[col].dropna().iloc[0] if len(X_train_clean[col].dropna()) > 0 else None
                    if sample_val is not None:
                        float(sample_val)  # Test if convertible
                        # If successful, convert entire column
                        X_train_clean[col] = pd.to_numeric(X_train_clean[col], errors='coerce')
                        X_test_clean[col] = pd.to_numeric(X_test_clean[col], errors='coerce')
                except (ValueError, TypeError, IndexError):
                    pass  # Keep as categorical if conversion fails
        
        # Fill NaN values: for numeric columns use median, for categorical use mode
        for col in X_train_clean.columns:
            if X_train_clean[col].isna().any() or X_test_clean[col].isna().any():
                if pd.api.types.is_numeric_dtype(X_train_clean[col]):
                    fill_value = X_train_clean[col].median()
                    if pd.isna(fill_value):
                        fill_value = 0  # Fallback to 0 if all values are NaN
                    X_train_clean[col] = X_train_clean[col].fillna(fill_value)
                    X_test_clean[col] = X_test_clean[col].fillna(fill_value)
                else:
                    # For categorical, use mode from training data
                    mode_values = X_train_clean[col].mode()
                    fill_value = mode_values[0] if len(mode_values) > 0 else ''
                    if fill_value == '':
                        # If no mode, use first non-null value
                        non_null = X_train_clean[col].dropna()
                        fill_value = non_null.iloc[0] if len(non_null) > 0 else ''
                    X_train_clean[col] = X_train_clean[col].fillna(fill_value)
                    X_test_clean[col] = X_test_clean[col].fillna(fill_value)
        
        # Ensure all columns are numeric (convert remaining object columns to numeric codes)
        for col in X_train_clean.columns:
            if X_train_clean[col].dtype == 'object':
                # Convert categorical to numeric codes using training data categories
                train_cat = pd.Categorical(X_train_clean[col])
                X_train_clean[col] = train_cat.codes
                # Use same categories for test data
                X_test_clean[col] = pd.Categorical(X_test_clean[col], categories=train_cat.categories).codes
        
        # Validate y_train before classifier training
        valid_labels = {0, 1}
        invalid_train_mask = ~y_train.isin(valid_labels)
        if invalid_train_mask.any():
            n_invalid = invalid_train_mask.sum()
            if logger:
                logger.update_step(f"⚠️  Fixing {n_invalid} invalid labels in y_train (found: {y_train[invalid_train_mask].unique()})")
            # Replace invalid labels with majority class in training data
            majority_class = y_train.value_counts().idxmax()
            if majority_class not in valid_labels:
                majority_class = 1  # Default fallback
            y_train = y_train.copy()
            y_train.loc[invalid_train_mask] = majority_class
        
        # Apply StandardScaler to normalize ALL features
        from sklearn.preprocessing import StandardScaler
        scaler = StandardScaler()
        
        # Fit scaler on training data only, then transform both train and test
        X_train_scaled = pd.DataFrame(
            scaler.fit_transform(X_train_clean),
            columns=X_train_clean.columns,
            index=X_train_clean.index
        )
        X_test_scaled = pd.DataFrame(
            scaler.transform(X_test_clean),
            columns=X_test_clean.columns,
            index=X_test_clean.index
        )
        
        if logger:
            logger.update_step(f"✅ Applied StandardScaler normalization to {len(X_train_clean.columns)} features")
        
        for clf_name, clf_model in clf_configs.items():
            if logger:
                logger.update_step(f"Training {clf_name}")
            
            # Train with normalized data
            clf_model.fit(X_train_scaled, y_train)
            
            # Predict with normalized test data
            y_pred = clf_model.predict(X_test_scaled)
            y_pred_proba = clf_model.predict_proba(X_test_scaled)[:, 1] if hasattr(clf_model, 'predict_proba') else None
            
            # Evaluate performance
            perf = metrics_eval.evaluate(y_test, y_pred, y_pred_proba)
            performance_metrics[clf_name] = perf
            
            # Evaluate fairness (only if sensitive attributes exist)
            if sensitive_test is not None and len(sensitive_test.columns) > 0:
                fair = fairness_eval.evaluate(y_test, y_pred, sensitive_test, use_aif360=False)
            else:
                # No sensitive attributes - return empty fairness metrics
                fair = {'dpd': 0.0, 'eod': 0.0, 'eo': 0.0}
            fairness_metrics[clf_name] = fair
            
            if logger:
                f1_default = perf.get('f1', 0)
                f1_calibrated = perf.get('f1_calibrated', f1_default)
                opt_thresh = perf.get('optimal_threshold', 0.5)
                logger.update_step(f"  {clf_name}: F1={f1_default:.4f} → F1@{opt_thresh:.2f}={f1_calibrated:.4f}")
        
        return performance_metrics, fairness_metrics
    
    def _aggregate_metrics(self, metrics_dict: Dict[str, Dict[str, float]]) -> Dict[str, float]:
        """Aggregate metrics across classifiers (compute mean)."""
        if not metrics_dict:
            return {}
        
        # Get all metric names
        all_metrics = set()
        for clf_metrics in metrics_dict.values():
            all_metrics.update(clf_metrics.keys())
        
        # Compute mean for each metric
        aggregated = {}
        for metric in all_metrics:
            values = [clf_metrics.get(metric, np.nan) 
                     for clf_metrics in metrics_dict.values()]
            aggregated[metric] = np.nanmean(values)
        
        return aggregated
    
    def _save_result(self, result: ExperimentResult):
        """Save experiment result to disk."""
        # Create output directory
        result_dir = self.output_dir / result.dataset / result.method
        result_dir.mkdir(parents=True, exist_ok=True)
        
        # Save as JSON
        json_path = result_dir / f"seed{result.seed}.json"
        with open(json_path, 'w') as f:
            json.dump(asdict(result), f, indent=2, default=str)
        
        # Save as pickle (for complex objects)
        pkl_path = result_dir / f"seed{result.seed}.pkl"
        with open(pkl_path, 'wb') as f:
            pickle.dump(result, f)
        
        if self.verbose:
            print(f"\n5. Results saved:")
            print(f"   - {json_path}")
            print(f"   - {pkl_path}")


    def _save_generated_samples_csv(
        self,
        X_train: pd.DataFrame,
        X_resampled: pd.DataFrame,
        y_resampled: pd.Series,
        dataset_name: str,
        method_name: str,
        seed: int,
        logger: Optional[ExperimentLogger] = None
    ):
        """Save generated samples and resampled dataset to CSV files."""
        try:
            # Create logs directory
            csv_dir = self.output_dir / "logs"
            csv_dir.mkdir(parents=True, exist_ok=True)
            
            # Extract only generated samples (exclude original training data)
            n_train = len(X_train)
            X_generated = X_resampled.iloc[n_train:].copy()
            y_generated = y_resampled.iloc[n_train:].copy()
            
            # Only save if there are generated samples
            if len(X_generated) == 0:
                if self.verbose:
                    print(f"   ⚠️  No generated samples to save for {method_name}")
                return
            
            # Add target column to generated samples DataFrame
            generated_df = X_generated.copy()
            generated_df['target'] = y_generated
            
            # Save generated samples (with target column)
            generated_csv = csv_dir / f"{dataset_name}_{method_name}_seed{seed}_generated_samples.csv"
            generated_df.to_csv(generated_csv, index=False)
            
            # Add target column to resampled dataset DataFrame
            resampled_df = X_resampled.copy()
            resampled_df['target'] = y_resampled
            
            # Save full resampled dataset (with target column)
            resampled_csv = csv_dir / f"{dataset_name}_{method_name}_seed{seed}_resampled_dataset.csv"
            resampled_df.to_csv(resampled_csv, index=False)
            
            if logger:
                logger.update_step(f"Saved CSV: {generated_csv.name}")
            
            if self.verbose:
                print(f"   💾 Saved generated samples: {generated_csv.name} ({len(generated_df)} samples)")
                print(f"   💾 Saved resampled dataset: {resampled_csv.name} ({len(resampled_df)} samples)")
        
        except Exception as e:
            if logger:
                logger.update_step(f"Warning: Failed to save CSV files: {str(e)}")
            if self.verbose:
                print(f"   ⚠️  Warning: Could not save CSV files: {str(e)}")
                import traceback
                traceback.print_exc()
    
    def _save_validated_samples_csv(
        self,
        X_generated: pd.DataFrame,
        y_generated: pd.Series,
        X_validated: pd.DataFrame,
        y_validated: pd.Series,
        dataset_name: str,
        method_name: str,
        seed: int
    ):
        """
        Save validated samples CSV for all methods (like QualSynth does).
        
        This creates a CSV file with only the validated samples that passed
        universal validation, making it easy to compare quality across methods.
        
        Args:
            X_generated: All generated samples (before validation)
            y_generated: Labels for generated samples
            X_validated: Validated samples (after validation)
            y_validated: Labels for validated samples
            dataset_name: Name of the dataset
            method_name: Name of the method
            seed: Random seed
        """
        try:
            # Create logs directory
            csv_dir = self.output_dir / "logs"
            csv_dir.mkdir(parents=True, exist_ok=True)
            
            # Only save if there are validated samples
            if len(X_validated) == 0:
                if self.verbose:
                    print(f"   ⚠️  No validated samples to save for {method_name}")
                return
            
            # Add target column to validated samples DataFrame
            validated_df = X_validated.copy()
            validated_df['target'] = y_validated.values
            
            # Save validated samples (with target column)
            validated_csv = csv_dir / f"{dataset_name}_{method_name}_seed{seed}_validated_samples.csv"
            validated_df.to_csv(validated_csv, index=False)
            
            # Calculate validation statistics
            n_generated = len(X_generated)
            n_validated = len(X_validated)
            validation_rate = (n_validated / n_generated * 100) if n_generated > 0 else 0.0
            
            if self.verbose:
                print(f"   ✅ Saved validated samples: {validated_csv.name}")
                print(f"      Generated: {n_generated} → Validated: {n_validated} ({validation_rate:.1f}% pass rate)")
        
        except Exception as e:
            if self.verbose:
                print(f"   ⚠️  Warning: Could not save validated CSV: {str(e)}")
                import traceback
                traceback.print_exc()


if __name__ == "__main__":
    # Test experiment runner
    print("="*70)
    print("Testing Experiment Runner")
    print("="*70)
    
    runner = ExperimentRunner(verbose=True)
    
    # Run a simple experiment
    print("\nRunning test experiment: adult + smote + seed42")
    result = runner.run_experiment(
        dataset_name='adult',
        method_name='smote',
        seed=42,
        save_results=True
    )
    
    print(f"\n✅ Test Complete")
    print(f"Success: {result.success}")
    print(f"Generated: {result.n_generated} samples")
    print(f"Avg F1: {result.avg_performance.get('f1', 0):.4f}")
    print(f"Avg DPD: {result.avg_fairness.get('demographic_parity_difference', 0):.4f}")

