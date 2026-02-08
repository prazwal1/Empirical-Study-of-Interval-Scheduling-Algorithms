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
    
    def run_quality_experiments(self, n_values=list(range(8, 21, 2)), trials=20):
        """Compare Greedy vs Optimal (for small n)"""
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
        
        for alpha in self.alphas:
            print(f"\nRunning quality experiments for α = {alpha}...")
            for n in n_values:
                eft_ratio, est_ratio, sd_ratio = [], [], []
                
                for _ in range(trials):
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
        self._save_quality_to_csv(results, n_values)
        
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
            n_values = [2**i for i in range(10, 20)]   # 1024 to ~500k
            
        results = {}
        for alpha in self.alphas:
            print(f"\nRunning greedy runtime experiments for α = {alpha}...")
            times_eft = []
            times_eft_std = []
            
            for n in n_values:
                trial_times = []
                for _ in range(trials):
                    jobs = generate_dataset(n, alpha)
                    
                    start = time.perf_counter()
                    EarliestFinishTime(jobs).schedule_jobs()
                    trial_times.append(time.perf_counter() - start)
                
                avg_time = np.mean(trial_times)
                std_time = np.std(trial_times, ddof=1) if len(trial_times) > 1 else 0.0
                times_eft.append(avg_time)
                times_eft_std.append(std_time)
                print(f"n={n:6d} | Time = {avg_time*1000:.3f}±{std_time*1000:.3f} ms")
            
            results[alpha] = {"n": n_values, "time": times_eft, "time_std": times_eft_std}
        
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
                    'time_seconds_mean': results[alpha]['time'][i],
                    'time_seconds_std': results[alpha]['time_std'][i]
                })
        df = pd.DataFrame(data)
        df.to_csv('data/greedy_runtime_results.csv', index=False)
        print("Greedy runtime results saved to data/greedy_runtime_results.csv")

    def run_exhaustive_runtime_experiments(self, n_values=None, trials=5):
        """Measure runtime of Exhaustive Algorithm"""
        if n_values is None:
            n_values = list(range(10, 21, 1))   # 10 to 20
            
        results = {}
        for alpha in self.alphas:
            print(f"\nRunning exhaustive runtime experiments for α = {alpha}...")
            times = []
            times_std = []
            
            for n in n_values:
                trial_times = []
                for _ in range(trials):
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
        n_values = list(range(8, 21, 2))
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
            plt.ylim(0.5, 1.05)
            plt.legend()
            plt.grid(True, alpha=0.3)
        plt.suptitle("Solution Quality: Greedy vs Optimal", fontsize=16)
        plt.tight_layout()
        plt.savefig("plots/quality_comparison.png", dpi=300)
        plt.show()

    def plot_greedy_big_o(self, results):
        plt.figure(figsize=(12, 5))
        
        # 6.1 Runtime t(n) vs n (log-log scale)
        plt.subplot(1, 2, 1)
        for alpha in self.alphas:
            plt.plot(results[alpha]["n"], results[alpha]["time"], 'o-', label=f"α={alpha}")
        plt.xscale('log')
        plt.yscale('log')
        plt.xlabel("n (log scale)")
        plt.ylabel("t(n) (log scale)")
        plt.title("Greedy Runtime vs n (log-log)")
        plt.legend()
        plt.grid(True)
        
        # Normalized runtime t(n) / (n log2 n)
        plt.subplot(1, 2, 2)
        for alpha in self.alphas:
            n_arr = np.array(results[alpha]["n"])
            t_arr = np.array(results[alpha]["time"])
            log_n = np.log2(n_arr + 1e-8)  # avoid div0
            normalized = t_arr / (n_arr * log_n)
            plt.plot(n_arr, normalized, 'o-', label=f"α={alpha}")
        plt.xscale('log')
        plt.xlabel("n (log scale)")
        plt.ylabel("t(n) / (n log2 n)")
        plt.title("Greedy Normalized Runtime")
        plt.legend()
        plt.grid(True)
        
        plt.tight_layout()
        plt.savefig("plots/greedy_big_o.png", dpi=300)
        plt.show()

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
        plt.show()