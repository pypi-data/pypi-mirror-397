"""
forecast_eval.py

Time Series Forecast Evaluation Script
Implements best-practice guidelines from systematic literature review.

Guidelines implemented:
  - Guideline 1: Baseline Comparison with Scale-Free Metrics (Gap 1)
  - Guideline 2: Stratified Performance Reporting (Gap 2)
    - 2a: Horizon Stratification (mandatory)
    - 2b: Regime Stratification (future/user extension)
    - 2c: Uncertainty Quantification (future/user extension)
  - Guideline 3: Statistical Significance Testing (Gap 3)

Gap mapping:
  - Gap 1: Missing Baseline Comparisons (59.6% of papers)
  - Gap 2: Over-Reliance on Aggregate Metrics (70.2% of papers)
  - Gap 3: Absence of Statistical Rigour (92% of papers)
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from scipy import stats


class ForecastEvaluator:
    """
    Comprehensive forecast evaluation following best-practice guidelines.
    
    Attributes:
        seasonal_period (int): Seasonal period for seasonal naive baseline
        results (dict): Dictionary storing evaluation results
    """
    
    def __init__(self, seasonal_period: int = 12):
        """
        Initialize evaluator.
        
        Args:
            seasonal_period: Period for seasonal patterns (e.g., 12 for monthly data)
        """
        self.seasonal_period = seasonal_period
        self.results = {}
    
    # =========================================================================
    # STANDARD METRICS (TOP-5)
    # =========================================================================
    
    def mse(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Mean Squared Error."""
        return np.mean((y_true - y_pred) ** 2)
    
    def rmse(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Root Mean Squared Error."""
        return np.sqrt(self.mse(y_true, y_pred))
    
    def mae(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Mean Absolute Error."""
        return np.mean(np.abs(y_true - y_pred))
    
    def mape(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Mean Absolute Percentage Error (%)."""
        epsilon = 1e-10
        return np.mean(np.abs((y_true - y_pred) / (y_true + epsilon))) * 100
    
    def nse(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """
        Nash-Sutcliffe Efficiency.
        NSE = 1 indicates perfect match.
        NSE = 0 indicates model is as good as mean baseline.
        NSE < 0 indicates model is worse than mean baseline.
        """
        numerator = np.sum((y_true - y_pred) ** 2)
        denominator = np.sum((y_true - np.mean(y_true)) ** 2)
        if denominator == 0:
            return np.nan
        return 1 - (numerator / denominator)
    
    # =========================================================================
    # GUIDELINE 1: BASELINE COMPARISON WITH SCALE-FREE METRICS (GAP 1)
    # =========================================================================
    
    def naive_baseline(self, y_train: np.ndarray, n_forecast: int, 
                       seasonal: bool = False) -> np.ndarray:
        """
        Generate naive baseline forecast.
        
        Args:
            y_train: Training data
            n_forecast: Number of forecasts to generate
            seasonal: If True, use seasonal naive; otherwise persistence
            
        Returns:
            Baseline forecast array
        """
        if seasonal and len(y_train) >= self.seasonal_period:
            # Seasonal naive: repeat last seasonal period
            return np.tile(
                y_train[-self.seasonal_period:],
                int(np.ceil(n_forecast / self.seasonal_period))
            )[:n_forecast]
        else:
            # Persistence: repeat last value
            return np.full(n_forecast, y_train[-1])
    
    def mase(self, y_true: np.ndarray, y_pred: np.ndarray,
             y_train: np.ndarray, seasonal: bool = False) -> float:
        """
        Mean Absolute Scaled Error (MASE).
        
        Formula: MASE = MAE_model / MAE_naive
        
        MASE < 1: Model outperforms naive baseline
        MASE = 1: Model equals naive baseline
        MASE > 1: Model underperforms naive baseline
        
        Args:
            y_true: Actual test values
            y_pred: Model predictions
            y_train: Training data (for scaling factor)
            seasonal: Use seasonal naive for scaling
            
        Returns:
            MASE value
        """
        mae_forecast = self.mae(y_true, y_pred)
        
        # Compute scaling factor from training data
        if seasonal and len(y_train) >= self.seasonal_period:
            naive_errors = np.abs(
                y_train[self.seasonal_period:] - y_train[:-self.seasonal_period]
            )
        else:
            naive_errors = np.abs(y_train[1:] - y_train[:-1])
        
        scaling_factor = np.mean(naive_errors)
        
        if scaling_factor == 0:
            return np.nan
        
        return mae_forecast / scaling_factor
    
    def skill_score(self, y_true: np.ndarray, y_pred: np.ndarray,
                    y_train: np.ndarray, metric: str = 'mae',
                    seasonal: bool = False) -> float:
        """
        Skill Score: SS = 1 - (Error_model / Error_baseline)
        
        SS > 0: Model better than baseline
        SS = 0: Model equal to baseline
        SS < 0: Model worse than baseline
        
        Args:
            y_true: Actual test values
            y_pred: Model predictions
            y_train: Training data
            metric: 'mae' or 'rmse'
            seasonal: Use seasonal naive baseline
            
        Returns:
            Skill score
        """
        y_baseline = self.naive_baseline(y_train, len(y_true), seasonal)
        
        if metric.lower() == 'mae':
            error_model = self.mae(y_true, y_pred)
            error_baseline = self.mae(y_true, y_baseline)
        elif metric.lower() == 'rmse':
            error_model = self.rmse(y_true, y_pred)
            error_baseline = self.rmse(y_true, y_baseline)
        else:
            raise ValueError(f"Unsupported metric: {metric}")
        
        if error_baseline == 0:
            return np.nan
        
        return 1 - (error_model / error_baseline)
    
    # =========================================================================
    # GUIDELINE 3: STATISTICAL SIGNIFICANCE TESTING (GAP 3)
    # =========================================================================
    
    def loss_series(self, y_true: np.ndarray, y_pred: np.ndarray,
                    y_train: np.ndarray,
                    metrics: List[str] = None) -> Dict[str, np.ndarray]:
        """
        Export per-timestep loss series for statistical testing.
        
        Enables Diebold-Mariano test and other forecast comparison procedures.
        
        Args:
            y_true: Actual test values
            y_pred: Predicted values
            y_train: Training data (for baseline computation)
            metrics: List of metrics to compute ('mae', 'rmse', 'mase', etc.)
            
        Returns:
            Dictionary with per-timestep loss arrays
        """
        if metrics is None:
            metrics = ['mae', 'rmse', 'mase']
        
        loss_dict = {}
        
        for metric in metrics:
            if metric == 'mae':
                loss_dict['mae'] = np.abs(y_true - y_pred)
            elif metric == 'rmse':
                # Store per-step squared error for DM test
                loss_dict['rmse'] = (y_true - y_pred) ** 2
            elif metric == 'mase':
                forecast_error = np.abs(y_true - y_pred)
                naive_errors = np.abs(y_train[1:] - y_train[:-1])
                scaling = np.mean(naive_errors)
                if scaling > 0:
                    loss_dict['mase'] = forecast_error / scaling
                else:
                    loss_dict['mase'] = forecast_error
            elif metric == 'mape':
                epsilon = 1e-10
                loss_dict['mape'] = np.abs((y_true - y_pred) / (y_true + epsilon))
            elif metric == 'nse':
                loss_dict['nse'] = (y_true - y_pred) ** 2
        
        return loss_dict
    
    def diebold_mariano_test(self, loss_series_1: np.ndarray,
                             loss_series_2: np.ndarray,
                             h: int = 1) -> Dict:
        """
        Diebold-Mariano test for equal predictive accuracy.
        
        Tests the null hypothesis H0: E[d_t] = 0 (equal accuracy)
        against H1: E[d_t] ≠ 0 (unequal accuracy)
        
        Test statistic: DM = mean(d) / sqrt(Var(mean(d)))
        where d_t = loss_1(t) - loss_2(t)
        
        Args:
            loss_series_1: Per-timestep losses from model 1
            loss_series_2: Per-timestep losses from model 2 (baseline)
            h: Forecast horizon (for autocorrelation adjustment)
            
        Returns:
            Dictionary with statistic, p-value, conclusion
        """
        d = loss_series_1 - loss_series_2
        mean_d = np.mean(d)
        n = len(d)
        
        # Variance with autocorrelation adjustment
        var_d = np.var(d, ddof=1)
        
        # Autocorrelation adjustment for multi-step forecasts
        if h > 1:
            gamma = []
            for k in range(1, h):
                if len(d) > k:
                    gamma_k = np.mean((d[:-k] - mean_d) * (d[k:] - mean_d))
                    gamma.append(gamma_k)
            var_d = var_d + 2 * np.sum(gamma)
        
        # Test statistic
        if var_d > 0:
            dm_stat = mean_d / np.sqrt(var_d / n)
        else:
            dm_stat = 0
        
        # Two-tailed p-value (using t-distribution for small samples)
        p_value = 2 * (1 - stats.t.cdf(np.abs(dm_stat), df=n-1))
        
        # Interpretation
        if p_value < 0.05:
            if mean_d < 0:
                conclusion = "Model 1 significantly BETTER than Model 2 (p < 0.05)"
                significant = True
            else:
                conclusion = "Model 1 significantly WORSE than Model 2 (p < 0.05)"
                significant = True
        else:
            conclusion = "No significant difference detected (p ≥ 0.05)"
            significant = False
        
        return {
            'statistic': dm_stat,
            'p_value': p_value,
            'mean_loss_diff': mean_d,
            'conclusion': conclusion,
            'significant': significant
        }
    
    # =========================================================================
    # COMPREHENSIVE EVALUATION FUNCTION
    # =========================================================================
    
    def evaluate(self, y_true: np.ndarray, y_pred: np.ndarray, 
                 y_train: np.ndarray, y_baseline: Optional[np.ndarray] = None,
                 seasonal: bool = False,
                 return_loss_series: bool = False,
                 stratify_by_horizon: bool = False,
                 horizon_indices: Optional[List[Tuple[int, int]]] = None) -> Dict:
        """
        Comprehensive forecast evaluation following best-practice guidelines.
        
        Args:
            y_true: Actual test values
            y_pred: Predicted values
            y_train: Training data (for baseline computation)
            y_baseline: Pre-computed baseline forecast (optional)
            seasonal: Use seasonal naive if True
            return_loss_series: If True, compute Guideline 3 (statistical tests)
            stratify_by_horizon: If True, compute Guideline 2a (horizon stratification)
            horizon_indices: List of (start, end) tuples for horizon windows
            
        Returns:
            Dictionary with comprehensive metrics organized by guideline
        """
        
        results = {}
        
        # Compute baseline if not provided
        if y_baseline is None:
            y_baseline = self.naive_baseline(y_train, len(y_true), seasonal=seasonal)
        
        # ===== PART 1: STANDARD METRICS =====
        results['Standard_Metrics'] = {
            'mse': self.mse(y_true, y_pred),
            'rmse': self.rmse(y_true, y_pred),
            'mae': self.mae(y_true, y_pred),
            'mape': self.mape(y_true, y_pred),
            'nse': self.nse(y_true, y_pred),
        }
        
        # ===== GUIDELINE 1: BASELINE COMPARISON WITH SCALE-FREE METRICS (GAP 1) =====
        results['Guideline_1_Baseline'] = {
            'mase': self.mase(y_true, y_pred, y_train, seasonal=seasonal),
            'mae_skill_score': self.skill_score(y_true, y_pred, y_train, 
                                            metric='mae', seasonal=seasonal),
            'rmse_skill_score': self.skill_score(y_true, y_pred, y_train, 
                                                metric='rmse', seasonal=seasonal),
            'baseline_mae': self.mae(y_true, y_baseline),
            'model_mae': self.mae(y_true, y_pred),
            # ADD THESE TWO LINES:
            'baseline_rmse': self.rmse(y_true, y_baseline),
            'model_rmse': self.rmse(y_true, y_pred),
    }
        
        # ===== GUIDELINE 2: STRATIFIED PERFORMANCE REPORTING (GAP 2) =====
        # Guideline 2a: Horizon Stratification (mandatory)
        results['Guideline_2_Stratification'] = {
            'horizon_stratified': {
                'mae': {},
                'rmse': {},
            },
            'regime_stratified': {},  # Future: Guideline 2b
            'uncertainty_stratified': {},  # Future: Guideline 2c
        }
        
        if stratify_by_horizon and horizon_indices:
            for h_idx, (start, end) in enumerate(horizon_indices):
                y_true_h = y_true[start:end]
                y_pred_h = y_pred[start:end]
                
                if len(y_true_h) > 0:
                    horizon_name = f'horizon_{h_idx}_steps_{start}-{end-1}'
                    results['Guideline_2_Stratification']['horizon_stratified']['mae'][horizon_name] = \
                        self.mae(y_true_h, y_pred_h)
                    results['Guideline_2_Stratification']['horizon_stratified']['rmse'][horizon_name] = \
                        self.rmse(y_true_h, y_pred_h)
        
        # ===== GUIDELINE 3: STATISTICAL SIGNIFICANCE TESTING (GAP 3) =====
        if return_loss_series:
            loss_series_data = self.loss_series(y_true, y_pred, y_train)
            baseline_loss_series = self.loss_series(y_true, y_baseline, y_train)
            
            dm_results = {}
            
            if 'mae' in loss_series_data and 'mae' in baseline_loss_series:
                dm_results['diebold_mariano_mae'] = self.diebold_mariano_test(
                    loss_series_data['mae'],
                    baseline_loss_series['mae']
                )
            
            if 'rmse' in loss_series_data and 'rmse' in baseline_loss_series:
                dm_results['diebold_mariano_rmse'] = self.diebold_mariano_test(
                    loss_series_data['rmse'],
                    baseline_loss_series['rmse']
                )
            
            results['Guideline_3_Statistical'] = {
                'loss_series_model': loss_series_data,
                'loss_series_baseline': baseline_loss_series,
                **dm_results,
            }
        
        self.results = results
        return results
    
    # =========================================================================
    # SUMMARY REPORT
    # =========================================================================
    
    def summary_report(self) -> str:
        """
        Generate human-readable summary report with detailed explanations.
        
        Report structure:
          PART 1: Standard Metrics Overview
          PART 2: Guideline-Based Evaluation (1, 2, 3)
          PART 3: Gaps Addressed & Final Recommendation
        """
        if not self.results:
            return "No evaluation results yet. Call evaluate(...) before summary_report()."
        
        line = "=" * 80
        subline = "-" * 80
        report = "\n" + line + "\n"
        report += "FORECAST EVALUATION REPORT\n"
        report += "Best-Practice Diagnostics for Time Series Forecasts\n"
        report += "Following systematic literature review guidelines\n"
        report += line + "\n\n"
        
        # =====================================================================
        # PART 1: STANDARD METRICS OVERVIEW
        # =====================================================================
        
        std = self.results.get("Standard_Metrics", {})
        mse_val = std.get('mse', np.nan)
        rmse_val = std.get('rmse', np.nan)
        mae_val = std.get('mae', np.nan)
        mape_val = std.get('mape', np.nan)
        nse_val = std.get('nse', np.nan)
        
        report += "PART 1: STANDARD METRICS OVERVIEW\n"
        report += subline + "\n"
        report += "These are the TOP-5 most commonly reported point forecast metrics.\n"
        report += "They provide a baseline understanding of model accuracy before applying\n"
        report += "best-practice guidelines for rigorous evaluation.\n\n"
        
        report += "Interpretation Guide:\n"
        report += "  • Lower is better for: MSE, RMSE, MAE, MAPE\n"
        report += "  • Higher is better for: NSE\n"
        report += "  • RMSE penalizes large errors more than MAE\n"
        report += "  • MAPE can be misleading with values near zero\n"
        report += "  • NSE compares model to predicting the mean\n\n"
        
        report += f"MSE  (Mean Squared Error):           {mse_val:.4f}\n"
        report += f"RMSE (Root Mean Squared Error):      {rmse_val:.4f}\n"
        report += f"MAE  (Mean Absolute Error):          {mae_val:.4f}\n"
        report += f"MAPE (Mean Absolute % Error):        {mape_val:.4f}%\n"
        report += f"NSE  (Nash-Sutcliffe Efficiency):    {nse_val:.4f}\n\n"
        
        # NSE interpretation
        if not np.isnan(nse_val):
            report += "NSE Interpretation: "
            if nse_val > 0.75:
                report += "EXCELLENT (NSE > 0.75) - Model explains >75% of variance.\n"
            elif nse_val > 0.5:
                report += "GOOD (NSE > 0.5) - Model explains >50% of variance.\n"
            elif nse_val > 0:
                report += "ACCEPTABLE (NSE > 0) - Model better than mean, but modest performance.\n"
            else:
                report += "POOR (NSE ≤ 0) - Model performs worse than simply predicting the mean.\n"
        
        # MAPE interpretation
        if not np.isnan(mape_val):
            report += "MAPE Interpretation: "
            if mape_val < 10:
                report += "HIGHLY ACCURATE (<10%) - Forecast errors are very small.\n"
            elif mape_val < 20:
                report += "GOOD ACCURACY (10-20%) - Reasonable forecasting performance.\n"
            elif mape_val < 50:
                report += "MODERATE ACCURACY (20-50%) - Significant but acceptable errors.\n"
            else:
                report += "POOR ACCURACY (>50%) - Large forecasting errors detected.\n"
        
        report += "\n"
        report += "IMPORTANT: These metrics alone are insufficient for rigorous evaluation.\n"
        report += "The following guidelines address critical gaps in forecast evaluation.\n\n"
        
        report += line + "\n\n"
        
        # =====================================================================
        # PART 2: GUIDELINE-BASED EVALUATION
        # =====================================================================
        
        report += "PART 2: GUIDELINE-BASED EVALUATION\n"
        report += line + "\n\n"
        
        # ----- GUIDELINE 1: BASELINE COMPARISON WITH SCALE-FREE METRICS (GAP 1) -----
        
        g1 = self.results.get("Guideline_1_Baseline", {})
        mase = g1.get("mase", np.nan)
        mae_skill = g1.get("mae_skill_score", np.nan)
        rmse_skill = g1.get("rmse_skill_score", np.nan)
        baseline_mae = g1.get("baseline_mae", np.nan)
        model_mae = g1.get("model_mae", np.nan)
        baseline_rmse = g1.get("baseline_rmse", np.nan)
        model_rmse = g1.get("model_rmse", np.nan)
        
        report += "GUIDELINE 1 – BASELINE COMPARISON WITH SCALE-FREE METRICS\n"
        report += "(Addresses Gap 1: Missing Baseline Comparisons)\n"
        report += subline + "\n\n"
        
        report += "WHY THIS MATTERS:\n"
        report += "59.6% of reviewed papers (112/188) fail to compare against naive baselines.\n"
        report += "Without this check, sophisticated models may be deployed despite failing to\n"
        report += "outperform trivial forecasting rules like 'repeat the last value'.\n\n"
        
        report += "This guideline uses two complementary approaches:\n"
        report += "  1. MASE (Mean Absolute Scaled Error) - embeds baseline by construction\n"
        report += "  2. Skill Scores - intuitive percentage improvement metric\n\n"
        
        report += subline + "\n"
        report += "MASE ANALYSIS\n"
        report += subline + "\n\n"
        
        report += f"MASE (Mean Absolute Scaled Error): {mase:.4f}\n\n"
        
        report += "What is MASE?\n"
        report += "MASE = MAE_model / MAE_naive_on_training_set\n"
        report += "It scales your model's error relative to a naive baseline, making it:\n"
        report += "  • Scale-free (comparable across different datasets)\n"
        report += "  • Interpretable (< 1 = beat baseline, > 1 = lost to baseline)\n"
        report += "  • Robust (handles zero values unlike MAPE)\n\n"
        
        report += "Your MASE Interpretation:\n"
        if mase < 0.5:
            report += f"  ★★★ EXCELLENT: MASE = {mase:.4f} < 0.5\n"
            report += "  Your model reduces naive baseline errors by more than 50%.\n"
            report += "  This represents substantial forecasting skill.\n"
        elif mase < 0.75:
            report += f"  ★★  VERY GOOD: MASE = {mase:.4f} (0.5-0.75)\n"
            report += "  Your model reduces naive baseline errors by 25-50%.\n"
            report += "  This indicates strong forecasting ability.\n"
        elif mase < 1.0:
            report += f"  ★   GOOD: MASE = {mase:.4f} (0.75-1.0)\n"
            report += "  Your model outperforms the naive baseline by up to 25%.\n"
            report += "  The model adds forecasting value.\n"
        elif mase < 1.25:
            report += f"  ⚠   MARGINAL: MASE = {mase:.4f} (1.0-1.25)\n"
            report += "  Your model slightly underperforms the naive baseline.\n"
            report += "  Deployment questionable - consider model improvements.\n"
        else:
            report += f"  ✗   POOR: MASE = {mase:.4f} > 1.25\n"
            report += "  Your model substantially underperforms the naive baseline.\n"
            report += "  Deployment NOT recommended - model requires major revision.\n"
        
        report += "\n" + subline + "\n"
        report += "SKILL SCORE ANALYSIS\n"
        report += subline + "\n\n"
        
        report += "What are Skill Scores?\n"
        report += "SS = 1 - (Error_model / Error_baseline)\n"
        report += "  • SS = 0.2 means 20% error reduction vs baseline\n"
        report += "  • SS = 0 means equal to baseline\n"
        report += "  • SS < 0 means worse than baseline\n\n"
        
        report += f"MAE of naive baseline:  {baseline_mae:.4f}\n"
        report += f"MAE of your model:      {model_mae:.4f}\n"
        report += f"MAE Skill Score:        {mae_skill:.4f} ({mae_skill*100:.1f}% improvement)\n\n"
        
        report += f"RMSE of naive baseline: {baseline_rmse:.4f}\n"
        report += f"RMSE of your model:     {model_rmse:.4f}\n"
        report += f"RMSE Skill Score:       {rmse_skill:.4f} ({rmse_skill*100:.1f}% improvement)\n\n"
        
        # Skill score interpretation
        if mae_skill > 0.2 and rmse_skill > 0.2:
            report += "Skill Score Interpretation: STRONG PERFORMANCE\n"
            report += "Both MAE and RMSE show >20% improvement over baseline.\n"
            report += "Your model demonstrates substantial forecasting skill.\n"
        elif mae_skill > 0.1 and rmse_skill > 0.1:
            report += "Skill Score Interpretation: MODERATE PERFORMANCE\n"
            report += "Both metrics show 10-20% improvement over baseline.\n"
            report += "Your model adds value but has room for improvement.\n"
        elif mae_skill > 0 and rmse_skill > 0:
            report += "Skill Score Interpretation: MARGINAL PERFORMANCE\n"
            report += "Both metrics show <10% improvement over baseline.\n"
            report += "Deployment may be justified but benefits are modest.\n"
        elif mae_skill > 0 or rmse_skill > 0:
            report += "Skill Score Interpretation: INCONSISTENT PERFORMANCE\n"
            report += "Mixed results - one metric beats baseline, other doesn't.\n"
            report += "Model may handle certain error types better than others.\n"
        else:
            report += "Skill Score Interpretation: UNDERPERFORMING\n"
            report += "Model fails to beat baseline on both MAE and RMSE.\n"
            report += "Deployment NOT recommended.\n"
        
        report += "\n" + subline + "\n"
        report += "GUIDELINE 1 CONCLUSION\n"
        report += subline + "\n\n"
        
        # Guideline 1 conclusion
        guideline_1_pass = (mase < 1) and (mae_skill > 0) and (rmse_skill > 0)
        
        report += "► OVERALL ASSESSMENT: "
        if guideline_1_pass and mase < 0.75:
            report += "★★★ STRONGLY PASS\n\n"
            report += "RESULT: Your model clearly and substantially outperforms the naïve baseline.\n\n"
            report += "EVIDENCE:\n"
            report += f"  • MASE = {mase:.4f} < 1.0 (beat baseline)\n"
            report += f"  • MAE skill = {mae_skill:.4f} > 0 ({mae_skill*100:.1f}% improvement)\n"
            report += f"  • RMSE skill = {rmse_skill:.4f} > 0 ({rmse_skill*100:.1f}% improvement)\n\n"
            report += "INTERPRETATION:\n"
            report += "The model demonstrates genuine predictive skill beyond capturing trivial\n"
            report += "patterns. All metrics consistently indicate superior performance. This model\n"
            report += "adds real forecasting value and satisfies Gap 1 requirements.\n\n"
            report += "RECOMMENDATION: Proceed with confidence to statistical testing (Guideline 3).\n\n"
        elif guideline_1_pass:
            report += "★★  PASS\n\n"
            report += "RESULT: Your model outperforms the naïve baseline.\n\n"
            report += "EVIDENCE:\n"
            report += f"  • MASE = {mase:.4f} < 1.0 (beat baseline)\n"
            report += f"  • MAE skill = {mae_skill:.4f} > 0 ({mae_skill*100:.1f}% improvement)\n"
            report += f"  • RMSE skill = {rmse_skill:.4f} > 0 ({rmse_skill*100:.1f}% improvement)\n\n"
            report += "INTERPRETATION:\n"
            report += "The model adds forecasting value beyond trivial methods. While improvements\n"
            report += "are modest, all metrics consistently support baseline superiority.\n"
            report += "Gap 1 requirements are satisfied.\n\n"
            report += "RECOMMENDATION: Proceed to statistical testing to validate significance.\n\n"
        elif (mase >= 1) and (mae_skill <= 0) and (rmse_skill <= 0):
            report += "✗   FAIL\n\n"
            report += "RESULT: Your model does NOT outperform the naïve baseline.\n\n"
            report += "EVIDENCE:\n"
            report += f"  • MASE = {mase:.4f} ≥ 1.0 (worse than or equal to baseline)\n"
            report += f"  • MAE skill = {mae_skill:.4f} ≤ 0 (no improvement)\n"
            report += f"  • RMSE skill = {rmse_skill:.4f} ≤ 0 (no improvement)\n\n"
            report += "INTERPRETATION:\n"
            report += "The model fails to capture patterns beyond what a trivial 'repeat last value'\n"
            report += "or seasonal naive forecast provides. Deploying this model would provide no\n"
            report += "benefit over simple baseline methods.\n\n"
            report += "RECOMMENDATION:\n"
            report += "  • Do NOT deploy - model requires fundamental improvements\n"
            report += "  • Investigate: feature engineering, model architecture, hyperparameters\n"
            report += "  • Consider: different model families, additional data sources\n\n"
        else:
            report += "⚠   MIXED RESULTS\n\n"
            report += "RESULT: Inconsistent evidence across metrics.\n\n"
            report += "EVIDENCE:\n"
            report += f"  • MASE = {mase:.4f}\n"
            report += f"  • MAE skill = {mae_skill:.4f}\n"
            report += f"  • RMSE skill = {rmse_skill:.4f}\n\n"
            report += "INTERPRETATION:\n"
            report += "Some metrics indicate improvement while others do not. This suggests the\n"
            report += "model may handle certain aspects of forecasting better than others (e.g.,\n"
            report += "reducing average errors but not large errors, or vice versa).\n\n"
            report += "RECOMMENDATION:\n"
            report += "  • Investigate: why performance is inconsistent\n"
            report += "  • Examine: residual plots, error distributions by horizon\n"
            report += "  • Consider: further tuning before deployment\n\n"
        
        report += line + "\n\n"
        
        # ----- GUIDELINE 2: STRATIFIED PERFORMANCE REPORTING (GAP 2) -----
        
        g2 = self.results.get("Guideline_2_Stratification", {})
        horizon_strat = g2.get("horizon_stratified", {})
        mae_strat = horizon_strat.get('mae', {})
        rmse_strat = horizon_strat.get('rmse', {})
        
        if mae_strat or rmse_strat:
            report += "GUIDELINE 2 – STRATIFIED PERFORMANCE REPORTING\n"
            report += "(Addresses Gap 2: Over-Reliance on Aggregate Metrics)\n"
            report += subline + "\n\n"
            
            report += "WHY THIS MATTERS:\n"
            report += "70.2% of reviewed papers (132/188) report only aggregate metrics.\n"
            report += "Aggregate metrics can mask critical failures at specific horizons or regimes.\n"
            report += "Example: A model with average RMSE of 8.3 MW might hide peak-period RMSE of 24.7 MW.\n\n"
            
            report += "Guideline 2 requires stratified reporting across three dimensions:\n"
            report += "  2a. Horizon Stratification (MANDATORY) - implemented below\n"
            report += "  2b. Regime Stratification (RECOMMENDED) - domain-specific, not implemented\n"
            report += "  2c. Uncertainty Quantification (RECOMMENDED) - requires probabilistic forecasts\n\n"
            
            report += subline + "\n"
            report += "GUIDELINE 2a: HORIZON STRATIFICATION\n"
            report += subline + "\n\n"
            
            report += "Stratified metrics reveal how performance changes across forecast horizons.\n"
            report += "This detects models that:\n"
            report += "  • Excel at short-term but fail at long-term forecasts\n"
            report += "  • Degrade systematically as horizon increases\n"
            report += "  • Have unpredictable performance variations\n\n"
            
            horizon_keys = sorted(mae_strat.keys())
            mae_values = [mae_strat[h] for h in horizon_keys]
            rmse_values = [rmse_strat[h] for h in horizon_keys]
            
            report += "PERFORMANCE BY HORIZON:\n"
            report += subline + "\n\n"
            
            for h in horizon_keys:
                mae_h = mae_strat[h]
                rmse_h = rmse_strat.get(h, np.nan)
                report += f"{h}:\n"
                report += f"  MAE:  {mae_h:.4f}\n"
                report += f"  RMSE: {rmse_h:.4f}\n\n"
            
            # Statistical analysis of variation
            report += subline + "\n"
            report += "VARIATION ANALYSIS\n"
            report += subline + "\n\n"
            
            if len(mae_values) > 1:
                mae_range = max(mae_values) - min(mae_values)
                mae_mean = np.mean(mae_values)
                mae_std = np.std(mae_values)
                relative_variation = mae_range / mae_mean if mae_mean > 0 else 0
                
                best_horizon = horizon_keys[np.argmin(mae_values)]
                worst_horizon = horizon_keys[np.argmax(mae_values)]
                
                report += f"MAE Statistics across horizons:\n"
                report += f"  Minimum:    {min(mae_values):.4f} (at {best_horizon})\n"
                report += f"  Maximum:    {max(mae_values):.4f} (at {worst_horizon})\n"
                report += f"  Mean:       {mae_mean:.4f}\n"
                report += f"  Std Dev:    {mae_std:.4f}\n"
                report += f"  Range:      {mae_range:.4f}\n"
                report += f"  Coefficient of Variation: {relative_variation:.2%}\n\n"
                
                report += "INTERPRETATION:\n"
                if relative_variation < 0.2:
                    report += "CONSISTENT PERFORMANCE (variation < 20%)\n"
                    report += "The model maintains stable accuracy throughout the forecast period.\n"
                    report += "This is ideal - performance does not degrade significantly with horizon.\n\n"
                    guideline_2_pass = True
                elif relative_variation < 0.5:
                    report += "MODERATE VARIATION (20-50%)\n"
                    report += "Performance shows noticeable differences across horizons.\n"
                    report += f"Best performance at: {best_horizon} (MAE = {min(mae_values):.4f})\n"
                    report += f"Worst performance at: {worst_horizon} (MAE = {max(mae_values):.4f})\n\n"
                    report += "CONCERN: The variation is significant enough to warrant attention.\n"
                    report += "Users should be aware that accuracy differs substantially by horizon.\n\n"
                    guideline_2_pass = False
                else:
                    report += "HIGH VARIATION (>50%)\n"
                    report += "⚠ WARNING: Performance varies dramatically across horizons.\n"
                    report += f"Best performance at: {best_horizon} (MAE = {min(mae_values):.4f})\n"
                    report += f"Worst performance at: {worst_horizon} (MAE = {max(mae_values):.4f})\n"
                    report += f"Performance degradation: {(max(mae_values)/min(mae_values) - 1)*100:.1f}%\n\n"
                    report += "CRITICAL ISSUE:\n"
                    report += "Aggregate metrics are masking serious performance problems at specific horizons.\n"
                    report += "The model may be unreliable at certain forecast distances despite good average performance.\n\n"
                    guideline_2_pass = False
                
                # Trend analysis
                if len(mae_values) >= 3:
                    # Simple trend check: compare first third vs last third
                    third = len(mae_values) // 3
                    early_mean = np.mean(mae_values[:third]) if third > 0 else mae_values[0]
                    late_mean = np.mean(mae_values[-third:]) if third > 0 else mae_values[-1]
                    degradation = (late_mean - early_mean) / early_mean if early_mean > 0 else 0
                    
                    report += "HORIZON TREND ANALYSIS:\n"
                    if degradation > 0.15:
                        report += f"⚠ DEGRADING: Performance worsens by {degradation*100:.1f}% from early to late horizons.\n"
                        report += "This suggests the model struggles to maintain accuracy at longer forecast distances.\n"
                    elif degradation < -0.15:
                        report += f"↑ IMPROVING: Performance improves by {abs(degradation)*100:.1f}% from early to late horizons.\n"
                        report += "This is unusual but suggests the model may perform better at longer ranges.\n"
                    else:
                        report += "→ STABLE: No systematic trend detected. Performance relatively stable across horizons.\n"
                    report += "\n"
                
                report += subline + "\n"
                report += "GUIDELINE 2a CONCLUSION\n"
                report += subline + "\n\n"
                
                report += "► OVERALL ASSESSMENT: "
                if guideline_2_pass:
                    report += "★★  PASS\n\n"
                    report += "RESULT: Performance is consistent across horizons (variation < 20%).\n\n"
                    report += "INTERPRETATION:\n"
                    report += "The model maintains stable accuracy throughout the forecast period.\n"
                    report += "Users can have confidence that aggregate metrics accurately represent\n"
                    report += "performance at all forecast distances. No hidden horizon-specific failures detected.\n\n"
                    report += "Gap 2 (stratification aspect) is adequately addressed.\n\n"
                else:
                    report += "⚠   PARTIAL PASS\n\n"
                    report += "RESULT: Significant performance variation detected across horizons.\n\n"
                    report += "INTERPRETATION:\n"
                    report += "While the model may have acceptable average performance, accuracy varies\n"
                    report += "substantially by forecast distance. Aggregate metrics provide an incomplete\n"
                    report += "picture of model capabilities.\n\n"
                    report += "RECOMMENDATION:\n"
                    report += "  • Report horizon-specific metrics in any publication or deployment documentation\n"
                    report += f"  • Pay special attention to worst-performing horizon: {worst_horizon}\n"
                    report += "  • Consider horizon-specific model tuning or ensemble methods\n"
                    report += "  • Inform users about accuracy differences by forecast distance\n\n"
            else:
                report += "INCOMPLETE – Only one horizon provided; cannot assess variation.\n"
                report += "For complete Guideline 2a evaluation, provide multiple horizon windows.\n\n"
                guideline_2_pass = None
            
            report += "NOTE: Guideline 2b (Regime Stratification) and 2c (Uncertainty Quantification)\n"
            report += "are not implemented in this base evaluation. Users can extend the script for:\n"
            report += "  • Peak vs off-peak performance analysis (Guideline 2b)\n"
            report += "  • High vs low volatility regime comparison (Guideline 2b)\n"
            report += "  • Probabilistic forecast evaluation (Guideline 2c: CRPS, Pinball Loss)\n\n"
            
            report += line + "\n\n"
        else:
            guideline_2_pass = None
            report += "GUIDELINE 2 – STRATIFIED PERFORMANCE REPORTING\n"
            report += "(Addresses Gap 2: Over-Reliance on Aggregate Metrics)\n"
            report += subline + "\n\n"
            report += "⊘ NOT EVALUATED: Horizon stratification was not enabled (stratify_by_horizon=False)\n\n"
            report += "To evaluate Guideline 2, re-run with:\n"
            report += "  stratify_by_horizon=True\n"
            report += "  horizon_indices=[(0, h1), (h1, h2), (h2, h3), ...]\n\n"
            report += line + "\n\n"
        
        # ----- GUIDELINE 3: STATISTICAL SIGNIFICANCE TESTING (GAP 3) -----
        
        g3 = self.results.get("Guideline_3_Statistical", {})
        if g3:
            report += "GUIDELINE 3 – STATISTICAL SIGNIFICANCE TESTING\n"
            report += "(Addresses Gap 3: Absence of Statistical Rigour)\n"
            report += subline + "\n\n"
            
            report += "WHY THIS MATTERS:\n"
            report += "Only 8% of reviewed papers (15/188) conduct significance testing.\n"
            report += "The M4 competition revealed that many methods showing apparent superiority\n"
            report += "had no statistically significant improvement when properly tested.\n\n"
            
            report += "Without statistical validation, you risk:\n"
            report += "  • Promoting improvements that are actually random noise\n"
            report += "  • Deploying models that won't replicate their performance\n"
            report += "  • Making decisions based on artifacts of the specific train-test split\n\n"
            
            report += "The Diebold-Mariano (DM) test answers: 'Is the performance difference between\n"
            report += "my model and the baseline real, or could it have occurred by chance?'\n\n"
            
            dm_mae = g3.get("diebold_mariano_mae", {})
            dm_rmse = g3.get("diebold_mariano_rmse", {})
            
            report += subline + "\n"
            report += "DIEBOLD-MARIANO TEST RESULTS\n"
            report += subline + "\n\n"
            
            if dm_mae:
                report += "Test 1: MAE-based comparison\n"
                report += subline + "\n\n"
                report += f"  Test Statistic: {dm_mae.get('statistic', np.nan):.4f}\n"
                report += f"  p-value:        {dm_mae.get('p_value', np.nan):.4f}\n"
                report += f"  Mean loss diff: {dm_mae.get('mean_loss_diff', np.nan):.4f}\n\n"
                
                report += "  Interpretation:\n"
                mae_pval = dm_mae.get('p_value', 1.0)
                mae_diff = dm_mae.get('mean_loss_diff', 0)
                
                if mae_pval < 0.01:
                    report += "  ★★★ HIGHLY SIGNIFICANT (p < 0.01)\n"
                    if mae_diff < 0:
                        report += "  Your model is SUBSTANTIALLY and SIGNIFICANTLY better than baseline.\n"
                        report += "  The probability this occurred by chance is less than 1%.\n"
                    else:
                        report += "  Your model is SIGNIFICANTLY worse than baseline (p < 0.01).\n"
                elif mae_pval < 0.05:
                    report += "  ★★  SIGNIFICANT (p < 0.05)\n"
                    if mae_diff < 0:
                        report += "  Your model is SIGNIFICANTLY better than baseline at the 5% level.\n"
                        report += "  The probability this occurred by chance is less than 5%.\n"
                    else:
                        report += "  Your model is SIGNIFICANTLY worse than baseline (p < 0.05).\n"
                elif mae_pval < 0.10:
                    report += "  ⚠   MARGINALLY SIGNIFICANT (p < 0.10)\n"
                    if mae_diff < 0:
                        report += "  Your model shows some evidence of being better, but not at conventional\n"
                        report += "  significance levels. Consider collecting more data or improving the model.\n"
                    else:
                        report += "  Your model shows some evidence of being worse (p < 0.10).\n"
                else:
                    report += "  ✗   NOT SIGNIFICANT (p ≥ 0.10)\n"
                    report += "  The observed performance difference could easily have occurred by chance.\n"
                    report += "  You have no statistical evidence that the model is better than baseline.\n"
                
                report += f"\n  Conclusion: {dm_mae.get('conclusion', 'N/A')}\n\n"
            
            if dm_rmse:
                report += "Test 2: RMSE-based comparison (squared error losses)\n"
                report += subline + "\n\n"
                report += f"  Test Statistic: {dm_rmse.get('statistic', np.nan):.4f}\n"
                report += f"  p-value:        {dm_rmse.get('p_value', np.nan):.4f}\n"
                report += f"  Mean loss diff: {dm_rmse.get('mean_loss_diff', np.nan):.4f}\n\n"
                
                report += "  Interpretation:\n"
                rmse_pval = dm_rmse.get('p_value', 1.0)
                rmse_diff = dm_rmse.get('mean_loss_diff', 0)
                
                if rmse_pval < 0.01:
                    report += "  ★★★ HIGHLY SIGNIFICANT (p < 0.01)\n"
                    if rmse_diff < 0:
                        report += "  Your model SIGNIFICANTLY reduces large errors compared to baseline.\n"
                    else:
                        report += "  Your model produces SIGNIFICANTLY larger errors than baseline (p < 0.01).\n"
                elif rmse_pval < 0.05:
                    report += "  ★★  SIGNIFICANT (p < 0.05)\n"
                    if rmse_diff < 0:
                        report += "  Your model SIGNIFICANTLY reduces squared errors at the 5% level.\n"
                    else:
                        report += "  Your model produces SIGNIFICANTLY larger squared errors (p < 0.05).\n"
                elif rmse_pval < 0.10:
                    report += "  ⚠   MARGINALLY SIGNIFICANT (p < 0.10)\n"
                    if rmse_diff < 0:
                        report += "  Some evidence of improvement in handling large errors, but not conclusive.\n"
                    else:
                        report += "  Some evidence of worse performance on large errors (p < 0.10).\n"
                else:
                    report += "  ✗   NOT SIGNIFICANT (p ≥ 0.10)\n"
                    report += "  No statistical evidence of difference in squared error performance.\n"
                
                report += f"\n  Conclusion: {dm_rmse.get('conclusion', 'N/A')}\n\n"
            
            # Guideline 3 conclusion
            mae_significant = dm_mae.get('significant', False) if dm_mae else False
            rmse_significant = dm_rmse.get('significant', False) if dm_rmse else False
            mae_better = dm_mae.get('mean_loss_diff', 0) < 0 if dm_mae else False
            rmse_better = dm_rmse.get('mean_loss_diff', 0) < 0 if dm_rmse else False
            
            report += subline + "\n"
            report += "GUIDELINE 3 CONCLUSION\n"
            report += subline + "\n\n"
            
            report += "► OVERALL ASSESSMENT: "
            if mae_significant and mae_better and rmse_significant and rmse_better:
                report += "★★★ STRONGLY PASS\n\n"
                report += "RESULT: Model superiority is STATISTICALLY SIGNIFICANT across both tests.\n\n"
                report += "EVIDENCE:\n"
                report += f"  • MAE test: p = {dm_mae.get('p_value', np.nan):.4f} < 0.05 (significant)\n"
                report += f"  • RMSE test: p = {dm_rmse.get('p_value', np.nan):.4f} < 0.05 (significant)\n"
                report += "  • Both tests show model is better (negative loss differential)\n\n"
                report += "INTERPRETATION:\n"
                report += "The observed performance improvements are extremely unlikely to be due to chance.\n"
                report += "Your model demonstrates:\n"
                report += "  • Significant reduction in average errors (MAE test)\n"
                report += "  • Significant reduction in large errors (RMSE test)\n"
                report += "  • Reproducible superiority that should hold on new data\n\n"
                report += "This provides STRONG STATISTICAL EVIDENCE for deployment.\n"
                report += "Gap 3 (statistical rigour) is fully satisfied.\n\n"
                guideline_3_pass = True
            elif (mae_significant and mae_better) or (rmse_significant and rmse_better):
                report += "★   PARTIAL PASS\n\n"
                report += "RESULT: Significant improvement on some but not all metrics.\n\n"
                report += "EVIDENCE:\n"
                report += f"  • MAE test: p = {dm_mae.get('p_value', np.nan):.4f} "
                report += f"({'significant' if mae_significant else 'not significant'})\n"
                report += f"  • RMSE test: p = {dm_rmse.get('p_value', np.nan):.4f} "
                report += f"({'significant' if rmse_significant else 'not significant'})\n\n"
                report += "INTERPRETATION:\n"
                if mae_significant and not rmse_significant:
                    report += "Your model significantly reduces average errors (MAE) but improvements in\n"
                    report += "handling large errors (RMSE) are not statistically confirmed. This suggests:\n"
                    report += "  • Reliable performance for typical forecasting situations\n"
                    report += "  • Less certain benefits during extreme events or large deviations\n\n"
                elif rmse_significant and not mae_significant:
                    report += "Your model significantly reduces large errors (RMSE) but average error\n"
                    report += "improvements (MAE) are not statistically confirmed. This suggests:\n"
                    report += "  • Strong performance during extreme events\n"
                    report += "  • Less certain benefits for typical forecast accuracy\n\n"
                report += "RECOMMENDATION:\n"
                report += "  • Deployment can be justified based on significant improvements\n"
                report += "  • Be aware of mixed statistical evidence\n"
                report += "  • Consider collecting more test data to strengthen conclusions\n\n"
                guideline_3_pass = False
            elif not (mae_significant or rmse_significant):
                report += "✗   FAIL\n\n"
                report += "RESULT: NO statistically significant differences detected.\n\n"
                report += "EVIDENCE:\n"
                report += f"  • MAE test: p = {dm_mae.get('p_value', np.nan):.4f} ≥ 0.05 (not significant)\n"
                report += f"  • RMSE test: p = {dm_rmse.get('p_value', np.nan):.4f} ≥ 0.05 (not significant)\n\n"
                report += "INTERPRETATION:\n"
                report += "While your model may show better raw metrics than the baseline, these\n"
                report += "improvements are not statistically distinguishable from random variation.\n"
                report += "This means:\n"
                report += "  • The observed improvements could be artifacts of this specific train-test split\n"
                report += "  • Performance may not replicate on new data\n"
                report += "  • You lack statistical evidence to claim genuine superiority\n\n"
                report += "POSSIBLE CAUSES:\n"
                report += "  • Insufficient test data (low statistical power)\n"
                report += "  • Model improvements are genuinely small\n"
                report += "  • High variance in forecast errors\n"
                report += "  • Model barely beats baseline\n\n"
                report += "RECOMMENDATION:\n"
                report += "  • Collect more test data to increase statistical power\n"
                report += "  • Further improve model to achieve larger performance gains\n"
                report += "  • Do NOT claim statistical superiority in publications\n"
                report += "  • Be cautious about deployment - benefits may not materialize\n\n"
                guideline_3_pass = False
            else:
                report += "⚠   MIXED RESULTS\n\n"
                report += "RESULT: Inconsistent statistical evidence.\n\n"
                report += "Review individual test results above for detailed interpretation.\n\n"
                guideline_3_pass = False
            
            report += line + "\n\n"
        else:
            guideline_3_pass = None
            report += "GUIDELINE 3 – STATISTICAL SIGNIFICANCE TESTING\n"
            report += "(Addresses Gap 3: Absence of Statistical Rigour)\n"
            report += subline + "\n\n"
            report += "⊘ NOT EVALUATED: Statistical testing was not enabled (return_loss_series=False)\n\n"
            report += "To evaluate Guideline 3, re-run with:\n"
            report += "  return_loss_series=True\n\n"
            report += "This will compute Diebold-Mariano tests to validate whether observed\n"
            report += "performance differences are statistically significant or due to chance.\n\n"
            report += line + "\n\n"
        
        # =====================================================================
        # PART 3: GAPS ADDRESSED & FINAL RECOMMENDATION
        # =====================================================================
        
        report += line + "\n"
        report += "PART 3: GAPS ADDRESSED & FINAL RECOMMENDATION\n"
        report += line + "\n\n"
        
        # Gap summary
        gap1_addressed = guideline_1_pass
        gap2_addressed = guideline_2_pass if guideline_2_pass is not None else False
        gap3_addressed = guideline_3_pass if guideline_3_pass is not None else False
        
        report += "SYSTEMATIC REVIEW GAPS SUMMARY\n"
        report += subline + "\n\n"
        
        report += "The systematic literature review identified three critical gaps in current\n"
        report += "forecast evaluation practices. Here's how your evaluation addresses them:\n\n"
        
        report += f"Gap 1 - Missing Baseline Comparisons (59.6% of papers):\n"
        report += f"  Status: {'✓ ADDRESSED' if gap1_addressed else '✗ NOT ADDRESSED'}\n"
        report += f"  Guideline 1 Result: {'PASS' if guideline_1_pass else 'FAIL'}\n"
        if gap1_addressed:
            report += "  Your model demonstrates genuine skill beyond trivial forecasting rules.\n"
        else:
            report += "  Your model fails to outperform naive baselines - fundamental issue.\n"
        report += "\n"
        
        if guideline_2_pass is not None:
            report += f"Gap 2 - Over-Reliance on Aggregate Metrics (70.2% of papers):\n"
            report += f"  Status: {'✓ ADDRESSED' if gap2_addressed else '✗ NOT ADDRESSED'}\n"
            report += f"  Guideline 2a (Horizon) Result: {'PASS' if guideline_2_pass else 'FAIL/PARTIAL'}\n"
            report += "  Guideline 2b (Regime): Not implemented (domain-specific)\n"
            report += "  Guideline 2c (Uncertainty): Not implemented (requires probabilistic forecasts)\n"
            if gap2_addressed:
                report += "  Stratified analysis confirms consistent performance across horizons.\n"
            else:
                report += "  Significant performance variation detected - aggregate metrics may mislead.\n"
        else:
            report += "Gap 2 - Over-Reliance on Aggregate Metrics (70.2% of papers):\n"
            report += "  Status: ⊘ NOT EVALUATED (stratify_by_horizon=False)\n"
            report += "  Enable horizon stratification to assess this gap.\n"
        report += "\n"
        
        if guideline_3_pass is not None:
            report += f"Gap 3 - Absence of Statistical Rigour (92% of papers):\n"
            report += f"  Status: {'✓ ADDRESSED' if gap3_addressed else '✗ NOT ADDRESSED'}\n"
            report += f"  Guideline 3 Result: {'PASS' if guideline_3_pass else 'FAIL/PARTIAL'}\n"
            if gap3_addressed:
                report += "  Statistical tests confirm improvements are significant, not random.\n"
            else:
                report += "  Improvements lack statistical significance - may be due to chance.\n"
        else:
            report += "Gap 3 - Absence of Statistical Rigour (92% of papers):\n"
            report += "  Status: ⊘ NOT EVALUATED (return_loss_series=False)\n"
            report += "  Enable loss series export to assess this gap.\n"
        report += "\n"
        
        report += subline + "\n"
        report += "FINAL DEPLOYMENT RECOMMENDATION\n"
        report += subline + "\n\n"
        
        # Count how many gaps are addressed
        gaps_addressed_count = sum([gap1_addressed, gap2_addressed, gap3_addressed])
        gaps_evaluated_count = sum([
            guideline_1_pass is not None,
            guideline_2_pass is not None,
            guideline_3_pass is not None
        ])
        
        if gap1_addressed and (gap3_addressed or guideline_3_pass is None):
            report += "✓✓✓ STRONGLY RECOMMENDED FOR DEPLOYMENT\n\n"
            report += "RATIONALE:\n"
            report += "  • Model clearly outperforms naive baseline (Gap 1: ✓)\n"
            if gap3_addressed:
                report += "  • Improvements are statistically significant (Gap 3: ✓)\n"
            if gap2_addressed:
                report += "  • Performance is consistent across horizons (Gap 2: ✓)\n"
            report += f"  • {gaps_addressed_count}/{gaps_evaluated_count} evaluated gaps successfully addressed\n\n"
            
            report += "CONFIDENCE LEVEL: HIGH\n"
            report += "Your model meets or exceeds best-practice evaluation standards.\n"
            report += "The evidence strongly supports deployment in production environments.\n\n"
            
            report += "DEPLOYMENT CHECKLIST:\n"
            report += "  ✓ Baseline comparison passed\n"
            if gap3_addressed:
                report += "  ✓ Statistical significance confirmed\n"
            if gap2_addressed:
                report += "  ✓ Stratified performance validated\n"
            report += "  ✓ No critical evaluation gaps remain\n\n"
            
        elif gap1_addressed and not gap3_addressed and guideline_3_pass is not None:
            report += "⚠⚠  CONDITIONALLY RECOMMENDED WITH CAVEATS\n\n"
            report += "RATIONALE:\n"
            report += "  • Model outperforms naive baseline (Gap 1: ✓)\n"
            report += "  • BUT improvements lack statistical significance (Gap 3: ✗)\n"
            if gap2_addressed:
                report += "  • Performance is consistent across horizons (Gap 2: ✓)\n"
            elif guideline_2_pass is not None:
                report += "  • Significant performance variation across horizons (Gap 2: ⚠)\n"
            report += f"  • {gaps_addressed_count}/{gaps_evaluated_count} evaluated gaps addressed\n\n"
            
            report += "CONFIDENCE LEVEL: MODERATE\n"
            report += "Your model shows promise but statistical evidence is weak.\n\n"
            
            report += "RECOMMENDATIONS BEFORE DEPLOYMENT:\n"
            report += "  1. Collect more test data to increase statistical power\n"
            report += "  2. Review stratified performance for hidden weaknesses\n"
            report += "  3. Consider whether observed improvements justify deployment costs\n"
            report += "  4. Implement monitoring to validate performance in production\n\n"
            
            report += "DEPLOYMENT DECISION:\n"
            report += "  • If deployment costs are low: PROCEED with monitoring\n"
            report += "  • If deployment costs are high: IMPROVE model first\n"
            report += "  • If accuracy is critical: COLLECT MORE DATA for validation\n\n"
            
        elif not gap1_addressed:
            report += "✗✗✗ NOT RECOMMENDED FOR DEPLOYMENT\n\n"
            report += "CRITICAL ISSUE:\n"
            report += "  ✗ Model FAILS to outperform naive baseline (Gap 1: ✗)\n\n"
            
            report += "INTERPRETATION:\n"
            report += "Your model does not demonstrate genuine forecasting skill beyond trivial methods.\n"
            report += "Deploying this model would provide no benefit over simple baseline approaches\n"
            report += "like 'repeat the last value' or seasonal naive forecasting.\n\n"
            
            report += "This is a FUNDAMENTAL FAILURE that must be addressed before deployment.\n\n"
            
            report += "REQUIRED ACTIONS:\n"
            report += "  1. DO NOT DEPLOY - model requires substantial improvements\n"
            report += "  2. Investigate root causes:\n"
            report += "     • Insufficient or poor-quality training data?\n"
            report += "     • Inappropriate model architecture for this problem?\n"
            report += "     • Poor feature engineering or data preprocessing?\n"
            report += "     • Hyperparameter tuning needed?\n"
            report += "  3. Consider alternative approaches:\n"
            report += "     • Different model families (ARIMA, exponential smoothing, other ML methods)\n"
            report += "     • Additional data sources or features\n"
            report += "     • Ensemble methods combining multiple models\n"
            report += "  4. Re-evaluate after improvements using this same rigorous framework\n\n"
            
            report += "NOTE: Until Gap 1 is addressed, statistical testing and stratification\n"
            report += "      are premature. Focus on achieving baseline superiority first.\n\n"
            
        else:
            report += "⚠⚠⚠ INSUFFICIENT EVALUATION - CANNOT RECOMMEND\n\n"
            report += "ISSUE:\n"
            report += "Critical evaluation components were not performed.\n\n"
            report += f"Gaps evaluated: {gaps_evaluated_count}/3\n"
            report += f"Gaps addressed: {gaps_addressed_count}/{gaps_evaluated_count}\n\n"
            
            report += "REQUIRED FOR COMPLETE EVALUATION:\n"
            if guideline_1_pass is None:
                report += "  • Enable baseline comparison (Guideline 1)\n"
            if guideline_2_pass is None:
                report += "  • Enable horizon stratification (Guideline 2a)\n"
            if guideline_3_pass is None:
                report += "  • Enable statistical testing (Guideline 3)\n"
            report += "\n"
            report += "Re-run evaluation with all components enabled for a complete assessment.\n\n"
        
        report += line + "\n"
        report += "END OF EVALUATION REPORT\n"
        report += line + "\n"
        
        return report
    
    def generate_html_report(self, output_path: str = "forecast_evaluation_report.html") -> str:
        """
        Generate interactive HTML report with collapsible sections.
        
        Args:
            output_path: Path to save the HTML file
            
        Returns:
            Path to the generated HTML file
        """
        if not self.results:
            raise ValueError("No evaluation results yet. Call evaluate(...) first.")
        
        # Get all the data
        std = self.results.get("Standard_Metrics", {})
        g1 = self.results.get("Guideline_1_Baseline", {})
        g2 = self.results.get("Guideline_2_Stratification", {})
        g3 = self.results.get("Guideline_3_Statistical", {})
        
        # Extract values
        mse_val = std.get('mse', np.nan)
        rmse_val = std.get('rmse', np.nan)
        mae_val = std.get('mae', np.nan)
        mape_val = std.get('mape', np.nan)
        nse_val = std.get('nse', np.nan)
        
        mase = g1.get("mase", np.nan)
        mae_skill = g1.get("mae_skill_score", np.nan)
        rmse_skill = g1.get("rmse_skill_score", np.nan)
        baseline_mae = g1.get("baseline_mae", np.nan)
        model_mae = g1.get("model_mae", np.nan)
        baseline_rmse = g1.get("baseline_rmse", np.nan)
        model_rmse = g1.get("model_rmse", np.nan)
        
        horizon_strat = g2.get("horizon_stratified", {})
        mae_strat = horizon_strat.get('mae', {})
        rmse_strat = horizon_strat.get('rmse', {})
        
        dm_mae = g3.get("diebold_mariano_mae", {}) if g3 else {}
        dm_rmse = g3.get("diebold_mariano_rmse", {}) if g3 else {}
        
        # Determine pass/fail status
        guideline_1_pass = (mase < 1) and (mae_skill > 0) and (rmse_skill > 0)
        
        guideline_2_pass = None
        if mae_strat:
            mae_values = list(mae_strat.values())
            if len(mae_values) > 1:
                mae_mean = np.mean(mae_values)
                mae_range = max(mae_values) - min(mae_values)
                relative_variation = mae_range / mae_mean if mae_mean > 0 else 0
                guideline_2_pass = relative_variation < 0.2
        
        guideline_3_pass = None
        if dm_mae and dm_rmse:
            mae_significant = dm_mae.get('significant', False)
            rmse_significant = dm_rmse.get('significant', False)
            mae_better = dm_mae.get('mean_loss_diff', 0) < 0
            rmse_better = dm_rmse.get('mean_loss_diff', 0) < 0
            guideline_3_pass = mae_significant and mae_better and rmse_significant and rmse_better
        
        # HTML Template
        html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Forecast Evaluation Report</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 20px;
                line-height: 1.6;
            }}
            
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                border-radius: 15px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.3);
                overflow: hidden;
            }}
            
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 40px;
                text-align: center;
            }}
            
            .header h1 {{
                font-size: 2.5em;
                margin-bottom: 10px;
            }}
            
            .header p {{
                font-size: 1.1em;
                opacity: 0.9;
            }}
            
            .content {{
                padding: 40px;
            }}
            
            .section {{
                margin-bottom: 30px;
                border: 1px solid #e0e0e0;
                border-radius: 10px;
                overflow: hidden;
                transition: all 0.3s ease;
            }}
            
            .section:hover {{
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            }}
            
            .section-header {{
                background: #f8f9fa;
                padding: 20px;
                cursor: pointer;
                display: flex;
                justify-content: space-between;
                align-items: center;
                user-select: none;
            }}
            
            .section-header:hover {{
                background: #e9ecef;
            }}
            
            .section-header h2 {{
                color: #333;
                font-size: 1.5em;
            }}
            
            .section-header .toggle {{
                font-size: 1.5em;
                font-weight: bold;
                color: #667eea;
            }}
            
            .section-content {{
                padding: 25px;
                display: none;
            }}
            
            .section-content.active {{
                display: block;
            }}
            
            .metric-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin: 20px 0;
            }}
            
            .metric-card {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                border-radius: 10px;
                text-align: center;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }}
            
            .metric-card h3 {{
                font-size: 0.9em;
                opacity: 0.9;
                margin-bottom: 10px;
            }}
            
            .metric-card .value {{
                font-size: 2em;
                font-weight: bold;
            }}
            
            .status-badge {{
                display: inline-block;
                padding: 8px 16px;
                border-radius: 20px;
                font-weight: bold;
                font-size: 0.9em;
                margin: 10px 5px;
            }}
            
            .status-pass {{
                background: #28a745;
                color: white;
            }}
            
            .status-fail {{
                background: #dc3545;
                color: white;
            }}
            
            .status-partial {{
                background: #ffc107;
                color: #333;
            }}
            
            .status-na {{
                background: #6c757d;
                color: white;
            }}
            
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
                background: white;
            }}
            
            th {{
                background: #667eea;
                color: white;
                padding: 12px;
                text-align: left;
            }}
            
            td {{
                padding: 12px;
                border-bottom: 1px solid #e0e0e0;
            }}
            
            tr:hover {{
                background: #f8f9fa;
            }}
            
            .info-box {{
                background: #e7f3ff;
                border-left: 4px solid #2196F3;
                padding: 15px;
                margin: 20px 0;
                border-radius: 5px;
            }}
            
            .warning-box {{
                background: #fff3cd;
                border-left: 4px solid #ffc107;
                padding: 15px;
                margin: 20px 0;
                border-radius: 5px;
            }}
            
            .success-box {{
                background: #d4edda;
                border-left: 4px solid #28a745;
                padding: 15px;
                margin: 20px 0;
                border-radius: 5px;
            }}
            
            .danger-box {{
                background: #f8d7da;
                border-left: 4px solid #dc3545;
                padding: 15px;
                margin: 20px 0;
                border-radius: 5px;
            }}
            
            .guideline-summary {{
                display: flex;
                justify-content: space-around;
                flex-wrap: wrap;
                gap: 20px;
                margin: 30px 0;
            }}
            
            .guideline-card {{
                flex: 1;
                min-width: 250px;
                background: white;
                border: 2px solid #e0e0e0;
                border-radius: 10px;
                padding: 20px;
                text-align: center;
            }}
            
            .guideline-card h3 {{
                color: #333;
                margin-bottom: 15px;
            }}
            
            .guideline-icon {{
                font-size: 3em;
                margin: 10px 0;
            }}
            
            .footer {{
                background: #f8f9fa;
                padding: 20px;
                text-align: center;
                color: #666;
                border-top: 1px solid #e0e0e0;
            }}
            
            @media print {{
                body {{
                    background: white;
                }}
                .section-content {{
                    display: block !important;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📊 Forecast Evaluation Report</h1>
                <p>Best-Practice Diagnostics for Time Series Forecasts</p>
                <p style="font-size: 0.9em; margin-top: 10px;">Generated on {np.datetime64('now')}</p>
            </div>
            
            <div class="content">
                
                <!-- Executive Summary -->
                <div class="section">
                    <div class="section-header" onclick="toggleSection(this)">
                        <h2>📋 Executive Summary</h2>
                        <span class="toggle">+</span>
                    </div>
                    <div class="section-content">
                        <div class="guideline-summary">
                            <div class="guideline-card">
                                <h3>Guideline 1</h3>
                                <div class="guideline-icon">{"✅" if guideline_1_pass else "❌"}</div>
                                <p><strong>Baseline Comparison</strong></p>
                                <span class="status-badge {'status-pass' if guideline_1_pass else 'status-fail'}">
                                    {"PASS" if guideline_1_pass else "FAIL"}
                                </span>
                            </div>
                            
                            <div class="guideline-card">
                                <h3>Guideline 2</h3>
                                <div class="guideline-icon">{"✅" if guideline_2_pass else "❓" if guideline_2_pass is None else "⚠️"}</div>
                                <p><strong>Stratified Reporting</strong></p>
                                <span class="status-badge {'status-pass' if guideline_2_pass else 'status-na' if guideline_2_pass is None else 'status-partial'}">
                                    {"PASS" if guideline_2_pass else "NOT EVALUATED" if guideline_2_pass is None else "PARTIAL"}
                                </span>
                            </div>
                            
                            <div class="guideline-card">
                                <h3>Guideline 3</h3>
                                <div class="guideline-icon">{"✅" if guideline_3_pass else "❓" if guideline_3_pass is None else "❌"}</div>
                                <p><strong>Statistical Testing</strong></p>
                                <span class="status-badge {'status-pass' if guideline_3_pass else 'status-na' if guideline_3_pass is None else 'status-fail'}">
                                    {"PASS" if guideline_3_pass else "NOT EVALUATED" if guideline_3_pass is None else "FAIL"}
                                </span>
                            </div>
                        </div>
                        
                        {'<div class="success-box"><strong>✓ RECOMMENDED FOR DEPLOYMENT</strong><br>Model meets best-practice evaluation standards.</div>' if guideline_1_pass and (guideline_3_pass or guideline_3_pass is None) else 
                        '<div class="warning-box"><strong>⚠ CONDITIONAL RECOMMENDATION</strong><br>Model shows promise but requires further validation.</div>' if guideline_1_pass else
                        '<div class="danger-box"><strong>✗ NOT RECOMMENDED FOR DEPLOYMENT</strong><br>Model fails to outperform naive baseline.</div>'}
                    </div>
                </div>
                
                <!-- Standard Metrics -->
                <div class="section">
                    <div class="section-header" onclick="toggleSection(this)">
                        <h2>📈 Standard Metrics</h2>
                        <span class="toggle">+</span>
                    </div>
                    <div class="section-content">
                        <p>Top-5 most commonly reported point forecast metrics:</p>
                        <div class="metric-grid">
                            <div class="metric-card">
                                <h3>MAE</h3>
                                <div class="value">{mae_val:.4f}</div>
                            </div>
                            <div class="metric-card">
                                <h3>RMSE</h3>
                                <div class="value">{rmse_val:.4f}</div>
                            </div>
                            <div class="metric-card">
                                <h3>MSE</h3>
                                <div class="value">{mse_val:.4f}</div>
                            </div>
                            <div class="metric-card">
                                <h3>MAPE (%)</h3>
                                <div class="value">{mape_val:.2f}</div>
                            </div>
                            <div class="metric-card">
                                <h3>NSE</h3>
                                <div class="value">{nse_val:.4f}</div>
                            </div>
                        </div>
                        <div class="info-box">
                            <strong>Note:</strong> These metrics alone are insufficient for rigorous evaluation. The following guidelines address critical gaps identified in systematic literature review.
                        </div>
                    </div>
                </div>
                
                <!-- Guideline 1 -->
                <div class="section">
                    <div class="section-header" onclick="toggleSection(this)">
                        <h2>🎯 Guideline 1: Baseline Comparison (Gap 1)</h2>
                        <span class="toggle">+</span>
                    </div>
                    <div class="section-content">
                        <p><strong>Addresses Gap 1:</strong> Missing Baseline Comparisons (59.6% of papers)</p>
                        
                        <h3 style="margin-top: 20px;">MASE Analysis</h3>
                        <div class="metric-grid">
                            <div class="metric-card">
                                <h3>MASE</h3>
                                <div class="value">{mase:.4f}</div>
                                <p style="margin-top: 10px; font-size: 0.9em;">
                                    {"✓ Beat baseline" if mase < 1 else "✗ Lost to baseline"}
                                </p>
                            </div>
                            <div class="metric-card">
                                <h3>MAE Skill Score</h3>
                                <div class="value">{mae_skill:.4f}</div>
                                <p style="margin-top: 10px; font-size: 0.9em;">
                                    {f"{mae_skill*100:.1f}% improvement"}
                                </p>
                            </div>
                            <div class="metric-card">
                                <h3>RMSE Skill Score</h3>
                                <div class="value">{rmse_skill:.4f}</div>
                                <p style="margin-top: 10px; font-size: 0.9em;">
                                    {f"{rmse_skill*100:.1f}% improvement"}
                                </p>
                            </div>
                        </div>
                        
                        <h3>Comparison Table</h3>
                        <table>
                            <tr>
                                <th>Metric</th>
                                <th>Baseline</th>
                                <th>Your Model</th>
                                <th>Improvement</th>
                            </tr>
                            <tr>
                                <td>MAE</td>
                                <td>{baseline_mae:.4f}</td>
                                <td>{model_mae:.4f}</td>
                                <td style="color: {'green' if model_mae < baseline_mae else 'red'}; font-weight: bold;">
                                    {((baseline_mae - model_mae) / baseline_mae * 100):.1f}%
                                </td>
                            </tr>
                            <tr>
                                <td>RMSE</td>
                                <td>{baseline_rmse:.4f}</td>
                                <td>{model_rmse:.4f}</td>
                                <td style="color: {'green' if model_rmse < baseline_rmse else 'red'}; font-weight: bold;">
                                    {((baseline_rmse - model_rmse) / baseline_rmse * 100):.1f}%
                                </td>
                            </tr>
                        </table>
                        
                        {'<div class="success-box"><strong>✓ PASS:</strong> Model clearly outperforms naive baseline. MASE < 1 and positive skill scores confirm genuine forecasting skill.</div>' if guideline_1_pass else
                        '<div class="danger-box"><strong>✗ FAIL:</strong> Model does not outperform naive baseline. Deployment NOT recommended.</div>'}
                    </div>
                </div>
                
                <!-- Guideline 2 -->
    """

        # Add Guideline 2 section
        if mae_strat:
            html_content += f"""
                <div class="section">
                    <div class="section-header" onclick="toggleSection(this)">
                        <h2>📊 Guideline 2: Stratified Performance (Gap 2)</h2>
                        <span class="toggle">+</span>
                    </div>
                    <div class="section-content">
                        <p><strong>Addresses Gap 2:</strong> Over-Reliance on Aggregate Metrics (70.2% of papers)</p>
                        
                        <h3>Performance by Horizon</h3>
                        <table>
                            <tr>
                                <th>Horizon</th>
                                <th>MAE</th>
                                <th>RMSE</th>
                            </tr>
    """
            for h_name in sorted(mae_strat.keys()):
                html_content += f"""
                            <tr>
                                <td>{h_name.replace('horizon_', 'Horizon ').replace('_steps_', ': steps ')}</td>
                                <td>{mae_strat[h_name]:.4f}</td>
                                <td>{rmse_strat.get(h_name, np.nan):.4f}</td>
                            </tr>
    """
            
            mae_values = list(mae_strat.values())
            if len(mae_values) > 1:
                mae_mean = np.mean(mae_values)
                mae_range = max(mae_values) - min(mae_values)
                relative_variation = mae_range / mae_mean if mae_mean > 0 else 0
                
                html_content += f"""
                        </table>
                        
                        <h3>Variation Analysis</h3>
                        <div class="metric-grid">
                            <div class="metric-card">
                                <h3>Min MAE</h3>
                                <div class="value">{min(mae_values):.4f}</div>
                            </div>
                            <div class="metric-card">
                                <h3>Max MAE</h3>
                                <div class="value">{max(mae_values):.4f}</div>
                            </div>
                            <div class="metric-card">
                                <h3>Variation</h3>
                                <div class="value">{relative_variation:.1%}</div>
                            </div>
                        </div>
                        
                        {'<div class="success-box"><strong>✓ CONSISTENT:</strong> Performance variation < 20%. Model maintains stable accuracy across horizons.</div>' if relative_variation < 0.2 else
                        '<div class="warning-box"><strong>⚠ MODERATE VARIATION:</strong> Performance varies by 20-50% across horizons. Review horizon-specific performance.</div>' if relative_variation < 0.5 else
                        '<div class="danger-box"><strong>✗ HIGH VARIATION:</strong> Performance varies by >50% across horizons. Aggregate metrics mask critical failures.</div>'}
                    </div>
                </div>
    """
        else:
            html_content += """
                <div class="section">
                    <div class="section-header" onclick="toggleSection(this)">
                        <h2>📊 Guideline 2: Stratified Performance (Gap 2)</h2>
                        <span class="toggle">+</span>
                    </div>
                    <div class="section-content">
                        <div class="info-box">
                            <strong>⊘ NOT EVALUATED:</strong> Horizon stratification was not enabled. Re-run with de>stratify_by_horizon=True</code>.
                        </div>
                    </div>
                </div>
    """

        # Add Guideline 3 section
        if dm_mae or dm_rmse:
            html_content += f"""
                <div class="section">
                    <div class="section-header" onclick="toggleSection(this)">
                        <h2>🔬 Guideline 3: Statistical Testing (Gap 3)</h2>
                        <span class="toggle">+</span>
                    </div>
                    <div class="section-content">
                        <p><strong>Addresses Gap 3:</strong> Absence of Statistical Rigour (92% of papers)</p>
                        
                        <h3>Diebold-Mariano Test Results</h3>
                        <table>
                            <tr>
                                <th>Test</th>
                                <th>Statistic</th>
                                <th>p-value</th>
                                <th>Result</th>
                            </tr>
    """
            if dm_mae:
                mae_pval = dm_mae.get('p_value', 1.0)
                html_content += f"""
                            <tr>
                                <td><strong>MAE-based</strong></td>
                                <td>{dm_mae.get('statistic', np.nan):.4f}</td>
                                <td style="color: {'green' if mae_pval < 0.05 else 'red'}; font-weight: bold;">
                                    {mae_pval:.4f}
                                </td>
                                <td>{dm_mae.get('conclusion', 'N/A')}</td>
                            </tr>
    """
            if dm_rmse:
                rmse_pval = dm_rmse.get('p_value', 1.0)
                html_content += f"""
                            <tr>
                                <td><strong>RMSE-based</strong></td>
                                <td>{dm_rmse.get('statistic', np.nan):.4f}</td>
                                <td style="color: {'green' if rmse_pval < 0.05 else 'red'}; font-weight: bold;">
                                    {rmse_pval:.4f}
                                </td>
                                <td>{dm_rmse.get('conclusion', 'N/A')}</td>
                            </tr>
    """
            
            mae_significant = dm_mae.get('significant', False) if dm_mae else False
            rmse_significant = dm_rmse.get('significant', False) if dm_rmse else False
            
            html_content += f"""
                        </table>
                        
                        {'<div class="success-box"><strong>✓ SIGNIFICANT:</strong> Performance improvements are statistically significant (p < 0.05). Strong evidence for deployment.</div>' if mae_significant and rmse_significant else
                        '<div class="warning-box"><strong>⚠ PARTIAL:</strong> Significant on some but not all metrics. Mixed statistical evidence.</div>' if mae_significant or rmse_significant else
                        '<div class="danger-box"><strong>✗ NOT SIGNIFICANT:</strong> Improvements could be due to chance (p ≥ 0.05). Insufficient statistical evidence.</div>'}
                    </div>
                </div>
    """
        else:
            html_content += """
                <div class="section">
                    <div class="section-header" onclick="toggleSection(this)">
                        <h2>🔬 Guideline 3: Statistical Testing (Gap 3)</h2>
                        <span class="toggle">+</span>
                    </div>
                    <div class="section-content">
                        <div class="info-box">
                            <strong>⊘ NOT EVALUATED:</strong> Statistical testing was not enabled. Re-run with de>return_loss_series=True</code>.
                        </div>
                    </div>
                </div>
    """

        # Close HTML
        html_content += """
            </div>
            
            <div class="footer">
                <p>Generated by ForecastEvaluator | Following systematic literature review guidelines</p>
                <p style="margin-top: 10px; font-size: 0.9em;">
                    Addresses 3 critical gaps: Baseline Comparison (59.6%), Aggregate Metrics (70.2%), Statistical Rigour (92%)
                </p>
            </div>
        </div>
        
        <script>
            function toggleSection(header) {
                const content = header.nextElementSibling;
                const toggle = header.querySelector('.toggle');
                
                if (content.classList.contains('active')) {
                    content.classList.remove('active');
                    toggle.textContent = '+';
                } else {
                    content.classList.add('active');
                    toggle.textContent = '−';
                }
            }
            
            // Auto-expand first section
            document.addEventListener('DOMContentLoaded', function() {
                const firstSection = document.querySelector('.section-header');
                if (firstSection) {
                    toggleSection(firstSection);
                }
            });
        </script>
    </body>
    </html>
    """
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"\n✓ HTML report generated: {output_path}")
        print(f"  Open in browser to view interactive report.")
        
        return output_path