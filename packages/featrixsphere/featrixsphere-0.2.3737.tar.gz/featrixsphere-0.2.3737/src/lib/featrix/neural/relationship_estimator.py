#!/usr/bin/env python3
"""
Fast estimation of pairwise column dependencies for attention head configuration.

Uses chi-squared tests on sampled pairs to estimate the number of dependent
column relationships without exhaustively testing all C(n,2) pairs.
"""
import logging
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)


def estimate_pairwise_dependency_count_fast(
    df: pd.DataFrame,
    *,
    n_pairs: int = 600,
    repeat: int = 5,
    max_pairs: int = 5_000,
    target_error: float = 0.03,
    n_bins: int = 8,
    lambda_storey: float = 0.8,
    min_joint_n: int = 30,
    random_state: int | None = None,
):
    """
    Fast estimate of #dependent column pairs.

    Approach:
      - Repeats 'repeat' times:
          - sample up to m pairs (without enumerating all C(p,2) pairs)
          - chi^2 independence on (possibly binned) contingency table
          - Storey estimator to infer π0 (null fraction), so edges ≈ (1-π0)*C(p,2)
      - Returns per-run results + median + [min,max] range

    Good for large p (hundreds/thousands): sampling is O(m), not O(p^2).
    
    Args:
        df: DataFrame to analyze
        n_pairs: Base number of pairs to sample per run (default: 600)
        repeat: Number of sampling runs (default: 5)
        max_pairs: Maximum pairs to test (default: 5000)
        target_error: Target margin of error for proportion estimation (default: 0.03)
        n_bins: Number of bins for quantizing numeric columns (default: 8)
        lambda_storey: Threshold for Storey estimator (default: 0.8)
        min_joint_n: Minimum samples required for chi-squared test (default: 30)
        random_state: Random seed for reproducibility
    
    Returns:
        dict with 'summary' and 'runs':
        - summary: Dict with median/min/max estimates
        - runs: List of individual run results
    """
    from scipy.stats import chi2_contingency
    
    rng = np.random.default_rng(random_state)

    cols = list(df.columns)
    p = len(cols)
    M = p * (p - 1) // 2
    if M == 0:
        return {
            "summary": dict(
                n_cols=p, total_pairs=0, estimated_edges_median=0,
                pi1_median=0.0, tested_pairs_median=0
            ),
            "runs": []
        }

    # Precompute dtype flags once
    is_num = {c: pd.api.types.is_numeric_dtype(df[c]) for c in cols}

    # Worst-case sample size for ±target_error on a proportion at 95% confidence
    m_required = int(np.ceil(0.25 * (1.96 / target_error) ** 2))
    m_base = max(n_pairs, m_required)
    m_base = min(max_pairs, M, m_base)

    def sample_unique_pairs(num_pairs: int, local_rng: np.random.Generator):
        """Sample unique unordered (i<j) pairs without enumerating all combinations."""
        seen = set()
        out = []
        # Oversample to reduce loop iterations
        while len(out) < num_pairs:
            need = num_pairs - len(out)
            i = local_rng.integers(0, p, size=need * 4)
            j = local_rng.integers(0, p, size=need * 4)
            for a, b in zip(i, j):
                if a == b:
                    continue
                if a > b:
                    a, b = b, a
                key = (a, b)
                if key in seen:
                    continue
                seen.add(key)
                out.append(key)
                if len(out) >= num_pairs:
                    break
        return out

    def run_once(seed_offset: int):
        local_rng = np.random.default_rng(None if random_state is None else random_state + seed_offset)

        # If small, just test all pairs
        if M <= m_base:
            pairs = [(i, j) for i in range(p) for j in range(i + 1, p)]
        else:
            pairs = sample_unique_pairs(m_base, local_rng)

        pvals = []
        tested = 0
        total_pairs = len(pairs)
        
        # Log progress every 25% or every 500 pairs, whichever is less frequent (to avoid spam)
        progress_interval = max(500, total_pairs // 4) if total_pairs > 1000 else max(100, total_pairs // 4)
        last_logged = 0

        for pair_idx, (i, j) in enumerate(pairs):
            # Log progress periodically
            if pair_idx > 0 and (pair_idx % progress_interval == 0 or pair_idx == total_pairs - 1):
                pct = (pair_idx / total_pairs) * 100
                logger.info(f"      Progress: {pair_idx+1}/{total_pairs} pairs ({pct:.0f}%)...")
                last_logged = pair_idx
            c1, c2 = cols[i], cols[j]
            x = df[c1]
            y = df[c2]

            mask = x.notna() & y.notna()
            if mask.sum() < min_joint_n:
                continue

            x = x[mask]
            y = y[mask]

            # Bin numeric columns into quantiles
            if is_num[c1]:
                try:
                    x = pd.qcut(x, q=n_bins, duplicates="drop")
                except (ValueError, TypeError):
                    continue
            else:
                # Bin high-cardinality categoricals/strings
                n_unique_x = x.nunique()
                if n_unique_x > n_bins * 2:  # High cardinality
                    # Use frequency-based binning: group rare values together
                    value_counts = x.value_counts()
                    # Top n_bins-1 values get their own bins, rest go to "OTHER"
                    top_values = value_counts.head(n_bins - 1).index
                    x = x.apply(lambda v: v if v in top_values else "__OTHER__")
            
            if is_num[c2]:
                try:
                    y = pd.qcut(y, q=n_bins, duplicates="drop")
                except (ValueError, TypeError):
                    continue
            else:
                # Bin high-cardinality categoricals/strings
                n_unique_y = y.nunique()
                if n_unique_y > n_bins * 2:  # High cardinality
                    value_counts = y.value_counts()
                    top_values = value_counts.head(n_bins - 1).index
                    y = y.apply(lambda v: v if v in top_values else "__OTHER__")

            tab = pd.crosstab(x, y)
            if tab.shape[0] < 2 or tab.shape[1] < 2:
                continue

            try:
                _, pval, _, _ = chi2_contingency(tab, correction=False)
            except Exception:
                continue

            pvals.append(pval)
            tested += 1

        if tested == 0:
            pi0_hat = 1.0
        else:
            pvals = np.asarray(pvals)
            pi0_hat = float(np.mean(pvals > lambda_storey) / (1.0 - lambda_storey))
            pi0_hat = float(np.clip(pi0_hat, 0.0, 1.0))

        pi1_hat = 1.0 - pi0_hat
        estimated_edges = int(round(pi1_hat * M))

        return dict(
            requested_pairs=m_base,
            tested_pairs=tested,
            pi0_hat=pi0_hat,
            pi1_hat=pi1_hat,
            estimated_edges=estimated_edges,
        )

    # Run estimation multiple times for robustness
    import time
    total_pairs_to_test = repeat * m_base
    logger.info(f"   Running {repeat} estimation runs, {m_base} pairs per run ({total_pairs_to_test} total pairs)...")
    logger.info(f"   Estimated time: ~{total_pairs_to_test * 0.001:.0f} seconds (rough estimate)")
    start_time = time.time()
    runs = []
    for r in range(repeat):
        run_start = time.time()
        logger.info(f"   Run {r+1}/{repeat}: Testing {m_base} pairs...")
        result = run_once(r)
        runs.append(result)
        run_elapsed = time.time() - run_start
        remaining_runs = repeat - (r + 1)
        estimated_remaining = run_elapsed * remaining_runs if remaining_runs > 0 else 0
        logger.info(f"   Run {r+1}/{repeat} complete: {result['tested_pairs']} pairs tested, {result['estimated_edges']} relationships detected ({run_elapsed:.1f}s)")
        if remaining_runs > 0:
            logger.info(f"      ~{estimated_remaining:.0f} seconds remaining")
    
    total_elapsed = time.time() - start_time
    logger.info(f"   ✅ All {repeat} runs complete in {total_elapsed:.1f} seconds")
    
    # Check if any runs completed successfully
    valid_runs = [r for r in runs if r['tested_pairs'] > 0]
    if not valid_runs:
        logger.error(f"💥 Relationship estimation FAILED: No valid chi-squared tests completed")
        logger.error(f"   All {repeat} runs failed to test any pairs")
        logger.error(f"   This indicates a serious data quality issue or bug")
        raise ValueError(f"Relationship estimation failed: no valid tests in {repeat} runs")
    
    if len(valid_runs) < repeat:
        logger.warning(f"⚠️  Only {len(valid_runs)}/{repeat} runs succeeded")

    edges = np.array([r["estimated_edges"] for r in valid_runs], dtype=float)
    pi1s  = np.array([r["pi1_hat"] for r in valid_runs], dtype=float)
    tested = np.array([r["tested_pairs"] for r in valid_runs], dtype=float)
    
    # Log per-run results for transparency
    logger.debug(f"   Run results: tested_pairs={tested.tolist()}, estimated_edges={edges.tolist()}")

    summary = dict(
        n_cols=p,
        total_pairs=M,
        repeat=repeat,
        successful_runs=len(valid_runs),
        requested_pairs_per_run=m_base,
        tested_pairs_median=int(np.median(tested)),
        tested_pairs_min=int(np.min(tested)),
        tested_pairs_max=int(np.max(tested)),
        pi1_median=float(np.median(pi1s)),
        pi1_min=float(np.min(pi1s)),
        pi1_max=float(np.max(pi1s)),
        estimated_edges_median=int(np.median(edges)),
        estimated_edges_min=int(np.min(edges)),
        estimated_edges_max=int(np.max(edges)),
        lambda_storey=lambda_storey,
        n_bins=n_bins,
        min_joint_n=min_joint_n,
        note="Estimated edges are 'pairwise dependence' count; indirect dependencies are included."
    )
    
    logger.debug(f"   ✅ Estimation complete: {summary['estimated_edges_median']} relationships detected")

    return {"summary": summary, "runs": runs}

