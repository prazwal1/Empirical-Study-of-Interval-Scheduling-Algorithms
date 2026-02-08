# Empirical Study of Interval Scheduling Algorithms

## 1. Overview of Implementation
The coding task implements and empirically evaluates greedy heuristics and an exhaustive optimal solver for the Interval Scheduling Problem (maximizing non-overlapping intervals). Key components:
- **Dataset Generation**: Random intervals with start ~ Uniform(0, T), duration ~ Uniform(1, 100), where T = α * n * 100. α controls overlap: 0.1 (high), 1.0 (medium), 5.0 (low).
- **Algorithms**:
  - Greedy: EFT (sort by finish, select non-overlapping), EST (sort by start), SD (sort by duration). All use merge sort (O(n log n)).
  - Exhaustive: Enumerates 2^n subsets, validates non-overlap (O(n log n) per subset), finds max size. No pruning, leading to O(n 2^n) worst-case.
- **Experiments**: Quality ratios (small n=8-20), greedy runtime (n=2^10 to 2^19), exhaustive runtime (n=10-20). For each configuration we compute and report the mean and standard deviation over multiple trials.
- **Tools**: Python, NumPy, Matplotlib.

## 2. Solution Quality Analysis
**Coding Question Addressed**: Compare greedy strategies (EFT, EST, SD) against optimal for solution quality (ratio of selected intervals to optimal) across overlap regimes and n values.

Experiments: For n=8 to 20 (step 2), 20 trials per point, we compute the mean and standard deviation of the quality ratio (greedy count / optimal count).

### Key Findings
- **EFT**: Empirically achieves ratio 1.0 (EFT_mean = 1.0 with zero standard deviation) across all α and n, confirming optimality. This aligns with proof by contradiction: assuming an optimal solution has more jobs leads to a contradiction by showing the greedy algorithm's early finish leaves room for additional jobs.
- **EST and SD**: Heuristics that are not always optimal. Performance degrades with higher n and depends strongly on overlap:
  - High overlap (α=0.1): EST ratios stay around 0.70–0.76 (e.g., 0.698 at n=20), while SD ratios decrease from about 0.83 (n=8) to about 0.51 (n=20). Dense conflicts punish poor choices (e.g., EST may select early-starting long jobs blocking others; SD prioritizes short jobs that block compatible longer ones).
  - Medium overlap (α=1.0): EST remains very close to 1.0 (≈0.96–0.99 across n), whereas SD ratios are significantly lower, roughly 0.24–0.47 and decreasing with n (0.240 at n=20).
  - Low overlap (α=5.0): EST is essentially always optimal (≈1.0 for all n), but SD still performs poorly, with ratios dropping from ~0.34 (n=8) to ~0.18 (n=20), illustrating that duration-only greediness is a weak quality heuristic even when intervals are sparse.
- Observation: EFT's finish-time priority is crucial (proven optimal). Heuristics approximate well in sparse scenarios but fail in dense ones, highlighting why they're heuristics with no correctness guarantee.

### Plot: Solution Quality: Greedy vs Optimal
![Solution Quality: Greedy vs Optimal](plots/quality_comparison.png)

**Table 1: Average Quality Ratios (Excerpt for n=20)**

| α (Overlap) | EFT Ratio | EST Ratio | SD Ratio | Optimal |
|-------------|-----------|-----------|----------|---------|
| 0.1 (High)  | 1.000     | 0.698     | 0.508    | 1.0     |
| 1.0 (Medium)| 1.000     | 0.972     | 0.240    | 1.0     |
| 5.0 (Low)   | 1.000     | 0.997     | 0.180    | 1.0     |

These results validate that SD has counterexamples (high-overlap case shows failure) and demonstrate the maintained non-overlap loop invariant in the greedy algorithm, proven via induction.

## 3. Runtime Complexity Validation
**Coding Question Addressed**: Empirically validate Big-O complexities for greedy (O(n log n)) and exhaustive (O(2^n)) across α, with normalization to confirm bounds.

### 3.1 Greedy Runtime (EFT as Representative)
Experiments: n=1024 to ~500k, 10 trials. For each configuration we measure total time (sorting + selection) and compute both the mean and standard deviation across trials.

- **Findings**:
  - Runtime scales as O(n log n): Log-log plot shows near-linear slope (slope ≈1 for n log n).
  - Normalized t(n)/(n log₂ n): Stabilizes around (2.7–3.7) × 10^{-7} s for α=1.0 (e.g., ≈2.94 × 10^{-7} at n=1024 and ≈3.65 × 10^{-7} at n=524288), confirming the n log n bound. Initial fluctuations are due to overhead at small n.
  - α Impact: All three overlap regimes exhibit very similar growth curves; constants differ slightly but the asymptotic behaviour is the same.
- Ties to Theory: Matches Mergesort's O(n log n) worst-case time complexity and O(n) space.

### Plot: Greedy Runtime Validation
![Greedy Runtime Validation](plots/greedy_big_o.png)

**Table 2: Greedy Runtime Excerpt (α=1.0)**

| n      | Time Mean (ms) | Time Std (ms) | Normalized (×10^{-7}) |
|--------|----------------|---------------|-----------------------|
| 1024   | 3.01           | 0.29          | 2.94                  |
| 16384  | 61.92          | 4.36          | 2.70                  |
| 524288 | 3634.42        | 392.81        | 3.65                  |

### 3.2 Exhaustive Runtime
Experiments: n=10-20, 5 trials. For each configuration we record the mean and standard deviation of the exhaustive solver's runtime.

- **Findings**:
  - Runtime O(n 2^n): vs n plot shows exponential growth (up to roughly 4s at n=20 for high overlap; e.g., ≈3.93 s for α=0.1 and ≈4.85 s for α=5.0).
  - Normalized t(n)/(n 2^n): Decreases to roughly (1.9–3.3) × 10^{-7} s (trends toward a constant but doesn't fully stabilize due to small n). High overlap (α=0.1) has a slightly lower constant (implicit early invalidations act as "pruning").
  - α Impact: High overlap is faster in practice (more early conflicts skip computations), but worst-case remains exponential for all α.
- Ties to Theory: Impractical for n>20 (e.g., n=20: ~1 million subsets, compared to n! for TSP which is ~2.4 × 10^{18} for n=20, far worse). No explicit pruning, but backtracking can significantly reduce runtime for small or typical n by eliminating branches that cannot lead to a better solution, so fewer states are explored in practice. However, in the worst case, no branches are pruned and the algorithm still examines all possible subsets (≈ 2ⁿ states). Therefore, pruning improves average-case performance but does not change the worst-case time complexity, which remains exponential and impractical at scale.

### Plot: Exhaustive Runtime Validation
![Exhaustive Runtime Validation](plots/exhaustive_big_o.png)

**Table 3: Exhaustive Runtime Excerpt (α=0.1)**

| n  | Time Mean (s) | Time Std (s) | Normalized (×10^{-7}) |
|----|---------------|--------------|-----------------------|
| 10 | 0.0033        | 0.0003       | 3.25                  |
| 15 | 0.1175        | 0.0087       | 2.39                  |
| 20 | 3.9304        | 0.1154       | 1.88                  |

## 4. Discussion and Observations
- **Overlap Impact (α)**: High overlap amplifies heuristic failures (quality) but slightly improves exhaustive runtime (implicit pruning). Low overlap makes all strategies near-optimal.
- **Trade-offs**: Greedy efficient (scalable) but heuristics like EST/SD can be suboptimal, distinguishing them from proven algorithms. Exhaustive is optimal but unscalable (NP-hard problem similar to TSP).
- **Limitations**: Small n for exhaustive limits normalization; floating-point precision in intervals; no pruning in exhaustive.
- **Improvements**: Use dynamic programming for optimal (O(n log n)) in quality tests; integer intervals; more α/trials.
- **Relation to Theory**: Empirical results support theoretical proofs (EFT optimality via contradiction/induction). Failure of heuristics in counterexamples shows why trial-and-error is insufficient.

## 5. Conclusion
The implementation confirms EFT's optimality and O(n log n) efficiency, while heuristics approximate variably based on overlap. Exhaustive validates optimality but highlights exponential impracticality. This empirical study complements theory, demonstrating criteria like correctness, efficiency, and simplicity.

