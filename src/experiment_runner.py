import time
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd  
import os  
from typing import List, Dict
from .dataset_generator import generate_dataset
from .greedy import EarliestFinishTime, EarlierStartTime, ShortestDuration
from .exhaustive import BruteForceScheduler

class ExperimentRunner:
    def __init__(self):
        self.alphas = [0.1, 1.0, 5.0]
        self.alpha_names = ["High Overlap", "Medium Overlap", "Low Overlap"]
        os.makedirs('data', exist_ok=True)  # Create data folder if not exists
    
    def run_quality_experiments(self, n_values=list(range(4, 21, 2)), trials=20):
        """Compare Greedy vs Optimal (for small n)"""
        # Ensure at least 10 trials for each (alpha, n) combination
        effective_trials = max(trials, 10)
        results = {
            alpha: {
                "EFT": [],
                "EFT_std": [],
                "EST": [],
                "EST_std": [],
                "SD": [],
                "SD_std": [],
                "Optimal": []
            }
            for alpha in self.alphas
        }
        # Keep track of which n values were actually used so plotting
        # can align x-axes even if n_values is customized.
        results_n_values = list(n_values)
        
        for alpha in self.alphas:
            print(f"\nRunning quality experiments for α = {alpha}...")
            for n in n_values:
                eft_ratio, est_ratio, sd_ratio = [], [], []

                # Warmup run (not recorded)
                warmup_jobs = generate_dataset(n, alpha)
                warmup_opt_scheduler = BruteForceScheduler(warmup_jobs)
                warmup_opt_jobs = warmup_opt_scheduler.schedule_jobs()
                _ = len(EarliestFinishTime(warmup_jobs).schedule_jobs())
                _ = len(EarlierStartTime(warmup_jobs).schedule_jobs())
                _ = len(ShortestDuration(warmup_jobs).schedule_jobs())

                for _ in range(effective_trials):
                    jobs = generate_dataset(n, alpha)
                    
                    # Exhaustive (Optimal)
                    opt_scheduler = BruteForceScheduler(jobs)
                    opt_jobs = opt_scheduler.schedule_jobs()
                    opt_count = len(opt_jobs)
                    
                    # Greedy Algorithms
                    eft_count = len(EarliestFinishTime(jobs).schedule_jobs())
                    est_count = len(EarlierStartTime(jobs).schedule_jobs())
                    sd_count  = len(ShortestDuration(jobs).schedule_jobs())
                    
                    eft_ratio.append(eft_count / opt_count if opt_count > 0 else 1.0)
                    est_ratio.append(est_count / opt_count if opt_count > 0 else 1.0)
                    sd_ratio.append(sd_count / opt_count if opt_count > 0 else 1.0)
                
                eft_mean = np.mean(eft_ratio)
                est_mean = np.mean(est_ratio)
                sd_mean = np.mean(sd_ratio)

                eft_std = np.std(eft_ratio, ddof=1) if len(eft_ratio) > 1 else 0.0
                est_std = np.std(est_ratio, ddof=1) if len(est_ratio) > 1 else 0.0
                sd_std = np.std(sd_ratio, ddof=1) if len(sd_ratio) > 1 else 0.0

                results[alpha]["EFT"].append(eft_mean)
                results[alpha]["EFT_std"].append(eft_std)
                results[alpha]["EST"].append(est_mean)
                results[alpha]["EST_std"].append(est_std)
                results[alpha]["SD"].append(sd_mean)
                results[alpha]["SD_std"].append(sd_std)
                results[alpha]["Optimal"].append(1.0)
                
                print(
                    f"n={n:2d} | "
                    f"EFT: {eft_mean:.3f}±{eft_std:.3f} | "
                    f"EST: {est_mean:.3f}±{est_std:.3f} | "
                    f"SD: {sd_mean:.3f}±{sd_std:.3f}"
                )
        
        # Save to CSV
        self._save_quality_to_csv(results, results_n_values)

        # Also attach n-values into the returned structure so plot_quality
        # can infer the correct x-axis length.
        results["n_values"] = results_n_values
        return results

    def _save_quality_to_csv(self, results, n_values):
        data = []
        for alpha in self.alphas:
            for i, n in enumerate(n_values):
                data.append({
                    'alpha': alpha,
                    'n': n,
                    'EFT_mean': results[alpha]['EFT'][i],
                    'EFT_std': results[alpha]['EFT_std'][i],
                    'EST_mean': results[alpha]['EST'][i],
                    'EST_std': results[alpha]['EST_std'][i],
                    'SD_mean': results[alpha]['SD'][i],
                    'SD_std': results[alpha]['SD_std'][i],
                    'Optimal': results[alpha]['Optimal'][i]
                })
        df = pd.DataFrame(data)
        df.to_csv('data/quality_results.csv', index=False)
        print("Quality results saved to data/quality_results.csv")

    def run_greedy_runtime_experiments(self, n_values=None, trials=10):
        """Measure runtime of Greedy Algorithms"""
        if n_values is None:
            n_values = [2**i for i in range(10, 21)]   # 1024 to ~1M
        
        # Ensure at least 10 trials for each (alpha, n) combination
        effective_trials = max(trials, 10)

        results = {}
        for alpha in self.alphas:
            print(f"\nRunning greedy runtime experiments for α = {alpha}...")
            times_eft = []
            times_eft_std = []
            times_est = []
            times_est_std = []
            times_sd = []
            times_sd_std = []
            
            for n in n_values:
                trial_times_eft = []
                trial_times_est = []
                trial_times_sd = []
                
                # Warmup run for each algorithm (not recorded)
                warmup_jobs = generate_dataset(n, alpha)
                start = time.perf_counter()
                EarliestFinishTime(warmup_jobs).schedule_jobs()
                _ = time.perf_counter() - start
                start = time.perf_counter()
                EarlierStartTime(warmup_jobs).schedule_jobs()
                _ = time.perf_counter() - start
                start = time.perf_counter()
                ShortestDuration(warmup_jobs).schedule_jobs()
                _ = time.perf_counter() - start

                for _ in range(effective_trials):
                    jobs = generate_dataset(n, alpha)
                    
                    start = time.perf_counter()
                    EarliestFinishTime(jobs).schedule_jobs()
                    trial_times_eft.append(time.perf_counter() - start)

                    start = time.perf_counter()
                    EarlierStartTime(jobs).schedule_jobs()
                    trial_times_est.append(time.perf_counter() - start)

                    start = time.perf_counter()
                    ShortestDuration(jobs).schedule_jobs()
                    trial_times_sd.append(time.perf_counter() - start)
                
                avg_time_eft = np.mean(trial_times_eft)
                std_time_eft = np.std(trial_times_eft, ddof=1) if len(trial_times_eft) > 1 else 0.0
                avg_time_est = np.mean(trial_times_est)
                std_time_est = np.std(trial_times_est, ddof=1) if len(trial_times_est) > 1 else 0.0
                avg_time_sd = np.mean(trial_times_sd)
                std_time_sd = np.std(trial_times_sd, ddof=1) if len(trial_times_sd) > 1 else 0.0

                times_eft.append(avg_time_eft)
                times_eft_std.append(std_time_eft)
                times_est.append(avg_time_est)
                times_est_std.append(std_time_est)
                times_sd.append(avg_time_sd)
                times_sd_std.append(std_time_sd)

                print(
                    f"n={n:6d} | "
                    f"EFT: {avg_time_eft*1000:.3f}±{std_time_eft*1000:.3f} ms | "
                    f"EST: {avg_time_est*1000:.3f}±{std_time_est*1000:.3f} ms | "
                    f"SD: {avg_time_sd*1000:.3f}±{std_time_sd*1000:.3f} ms"
                )
            
            results[alpha] = {
                "n": n_values,
                "EFT_time": times_eft,
                "EFT_time_std": times_eft_std,
                "EST_time": times_est,
                "EST_time_std": times_est_std,
                "SD_time": times_sd,
                "SD_time_std": times_sd_std,
            }
        
        # Save to CSV
        self._save_greedy_runtime_to_csv(results)
        
        return results

    def _save_greedy_runtime_to_csv(self, results):
        data = []
        for alpha in self.alphas:
            for i, n in enumerate(results[alpha]['n']):
                data.append({
                    'alpha': alpha,
                    'n': n,
                    'EFT_time_seconds_mean': results[alpha]['EFT_time'][i],
                    'EFT_time_seconds_std': results[alpha]['EFT_time_std'][i],
                    'EST_time_seconds_mean': results[alpha]['EST_time'][i],
                    'EST_time_seconds_std': results[alpha]['EST_time_std'][i],
                    'SD_time_seconds_mean': results[alpha]['SD_time'][i],
                    'SD_time_seconds_std': results[alpha]['SD_time_std'][i],
                })
        df = pd.DataFrame(data)
        df.to_csv('data/greedy_runtime_results.csv', index=False)
        print("Greedy runtime results saved to data/greedy_runtime_results.csv")

    def run_exhaustive_runtime_experiments(self, n_values=None, trials=10):
        """Measure runtime of Exhaustive Algorithm"""
        if n_values is None:
            n_values = list(range(5, 21, 1))   # 5 to 20
        
        # Ensure at least 10 trials for each (alpha, n) combination
        effective_trials = max(trials, 10)

        results = {}
        for alpha in self.alphas:
            print(f"\nRunning exhaustive runtime experiments for α = {alpha}...")
            times = []
            times_std = []
            
            for n in n_values:
                trial_times = []
                
                # Warmup run (not recorded)
                warmup_jobs = generate_dataset(n, alpha)
                start = time.perf_counter()
                BruteForceScheduler(warmup_jobs).schedule_jobs()
                _ = time.perf_counter() - start

                for _ in range(effective_trials):
                    jobs = generate_dataset(n, alpha)
                    
                    start = time.perf_counter()
                    BruteForceScheduler(jobs).schedule_jobs()
                    trial_times.append(time.perf_counter() - start)
                
                avg_time = np.mean(trial_times)
                std_time = np.std(trial_times, ddof=1) if len(trial_times) > 1 else 0.0
                times.append(avg_time)
                times_std.append(std_time)
                print(f"n={n:2d} | Time = {avg_time:.3f}±{std_time:.3f} s")
            
            results[alpha] = {"n": n_values, "time": times, "time_std": times_std}
        
        # Save to CSV
        self._save_exhaustive_runtime_to_csv(results)
        
        return results

    def _save_exhaustive_runtime_to_csv(self, results):
        data = []
        for alpha in self.alphas:
            for i, n in enumerate(results[alpha]['n']):
                data.append({
                    'alpha': alpha,
                    'n': n,
                    'time_seconds_mean': results[alpha]['time'][i],
                    'time_seconds_std': results[alpha]['time_std'][i]
                })
        df = pd.DataFrame(data)
        df.to_csv('data/exhaustive_runtime_results.csv', index=False)
        print("Exhaustive runtime results saved to data/exhaustive_runtime_results.csv")

    def plot_quality(self, results):
        # Prefer n-values recorded by run_quality_experiments; fallback to
        # the original default range if not present (for backward-compat).
        n_values = results.get("n_values", list(range(8, 21, 2)))
        plt.figure(figsize=(12, 7))
        for i, alpha in enumerate(self.alphas):
            plt.subplot(1, 3, i+1)
            plt.plot(n_values, results[alpha]["EFT"], 'o-', label="EFT", linewidth=2)
            plt.plot(n_values, results[alpha]["EST"], 's-', label="EST")
            plt.plot(n_values, results[alpha]["SD"],  '^-', label="Shortest Duration")
            plt.plot(n_values, results[alpha]["Optimal"], 'k--', label="Optimal")
            plt.title(f"α = {alpha} ({self.alpha_names[i]})")
            plt.xlabel("Number of intervals (n)")
            plt.ylabel("Ratio to Optimal")
            plt.ylim(0.0, 1.05)
            plt.legend()
            plt.grid(True, alpha=0.3)
        plt.suptitle("Solution Quality: Greedy vs Optimal", fontsize=16)
        plt.tight_layout()
        plt.savefig("plots/quality_comparison.png", dpi=300)

    def plot_greedy_big_o(self, results):
        algorithms = ["EFT", "EST", "SD"]
        colors = {"EFT": "tab:blue", "EST": "tab:orange", "SD": "tab:green"}
        markers = {"EFT": "o", "EST": "s", "SD": "^"}

        fig, axes = plt.subplots(2, len(self.alphas), figsize=(5 * len(self.alphas), 8), sharex='col')

        for col, alpha in enumerate(self.alphas):
            n_arr = np.array(results[alpha]["n"])

            # Row 0: Runtime t(n) vs n (log-log scale)
            ax_raw = axes[0, col]
            for algo in algorithms:
                t_arr = np.array(results[alpha][f"{algo}_time"])
                ax_raw.plot(
                    n_arr,
                    t_arr,
                    marker=markers[algo],
                    color=colors[algo],
                    label=algo,
                )
            ax_raw.set_xscale('log')
            ax_raw.set_yscale('log')
            ax_raw.set_title(f"α = {alpha} ({self.alpha_names[col]})")
            ax_raw.grid(True)
            if col == 0:
                ax_raw.set_ylabel("t(n) (log-log)")

            # Row 1: Normalized runtime t(n) / (n log2 n)
            ax_norm = axes[1, col]
            log_n = np.log2(n_arr + 1e-8)  # avoid div0
            for algo in algorithms:
                t_arr = np.array(results[alpha][f"{algo}_time"])
                normalized = t_arr / (n_arr * log_n)
                ax_norm.plot(
                    n_arr,
                    normalized,
                    marker=markers[algo],
                    color=colors[algo],
                    label=algo,
                )
            ax_norm.set_xscale('log')
            ax_norm.grid(True)
            ax_norm.set_xlabel("n (log scale)")
            if col == 0:
                ax_norm.set_ylabel("t(n) / (n log2 n)")

        # Single shared legend for algorithms, placed below the subplots
        handles, labels = axes[0, 0].get_legend_handles_labels()
        fig.legend(handles, labels, loc='lower center', ncol=len(algorithms), bbox_to_anchor=(0.5, 0.02))
        fig.suptitle("Greedy Runtime vs n for EFT, EST, and SD", fontsize=16, y=0.98)

        # Leave space at the bottom for the shared legend
        plt.tight_layout(rect=[0, 0.06, 1, 0.94])
        plt.savefig("plots/greedy_big_o.png", dpi=300)

    def plot_greedy_big_o_from_csv(self, csv_path: str = "data/greedy_runtime_results.csv"):
        """Re-generate greedy runtime plots directly from a saved CSV.

        This avoids any Pandas index on the x-axis by explicitly using the
        'n' column, and plots all three algorithms (EFT, EST, SD) with
        consistent colors and markers.
        """

        df = pd.read_csv(csv_path)

        algorithms = ["EFT", "EST", "SD"]
        colors = {"EFT": "tab:blue", "EST": "tab:orange", "SD": "tab:green"}
        markers = {"EFT": "o", "EST": "s", "SD": "^"}

        fig, axes = plt.subplots(2, len(self.alphas), figsize=(5 * len(self.alphas), 8), sharex="col")

        for col, alpha in enumerate(self.alphas):
            df_alpha = df[df["alpha"] == alpha].sort_values("n")
            n_arr = df_alpha["n"].to_numpy()

            # Row 0: Runtime t(n) vs n (log-log scale)
            ax_raw = axes[0, col]
            for algo in algorithms:
                t_arr = df_alpha[f"{algo}_time_seconds_mean"].to_numpy()
                ax_raw.plot(
                    n_arr,
                    t_arr,
                    marker=markers[algo],
                    color=colors[algo],
                    label=algo,
                )
            ax_raw.set_xscale("log")
            ax_raw.set_yscale("log")
            ax_raw.set_title(f"α = {alpha} ({self.alpha_names[col]})")
            ax_raw.grid(True)
            if col == 0:
                ax_raw.set_ylabel("t(n) (log-log)")

            # Row 1: Normalized runtime t(n) / (n log2 n)
            ax_norm = axes[1, col]
            log_n = np.log2(n_arr + 1e-8)  # avoid div0
            for algo in algorithms:
                t_arr = df_alpha[f"{algo}_time_seconds_mean"].to_numpy()
                normalized = t_arr / (n_arr * log_n)
                ax_norm.plot(
                    n_arr,
                    normalized,
                    marker=markers[algo],
                    color=colors[algo],
                    label=algo,
                )
            ax_norm.set_xscale("log")
            ax_norm.grid(True)
            ax_norm.set_xlabel("n (log scale)")
            if col == 0:
                ax_norm.set_ylabel("t(n) / (n log2 n)")

        handles, labels = axes[0, 0].get_legend_handles_labels()
        fig.legend(handles, labels, loc="lower center", ncol=len(algorithms), bbox_to_anchor=(0.5, 0.02))
        fig.suptitle("Greedy Runtime vs n for EFT, EST, and SD", fontsize=16, y=0.98)

        plt.tight_layout(rect=[0, 0.06, 1, 0.94])
        plt.savefig("plots/greedy_big_o_from_csv.png", dpi=300)

    def plot_exhaustive_big_o(self, results):
        plt.figure(figsize=(12, 5))
        
        # 6.2 Runtime t(n) vs n
        plt.subplot(1, 2, 1)
        for alpha in self.alphas:
            plt.plot(results[alpha]["n"], results[alpha]["time"], 'o-', label=f"α={alpha}")
        plt.xlabel("n")
        plt.ylabel("t(n) (seconds)")
        plt.title("Exhaustive Runtime vs n")
        plt.legend()
        plt.grid(True)
        
        # Normalized runtime t(n) / (n 2^n)
        plt.subplot(1, 2, 2)
        for alpha in self.alphas:
            n_arr = np.array(results[alpha]["n"])
            t_arr = np.array(results[alpha]["time"])
            exp_term = n_arr * (2 ** n_arr)
            normalized = t_arr / (exp_term + 1e-8)
            plt.plot(n_arr, normalized, 'o-', label=f"α={alpha}")
        plt.xlabel("n")
        plt.ylabel("t(n) / (n 2^n)")
        plt.title("Exhaustive Normalized Runtime")
        plt.legend()
        plt.grid(True)
        
        plt.tight_layout()
        plt.savefig("plots/exhaustive_big_o.png", dpi=300)
