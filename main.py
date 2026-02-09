# # main.py
# from src.experiment_runner import ExperimentRunner

# if __name__ == "__main__":
#     runner = ExperimentRunner()
    
#     print("=== Starting Interval Scheduling Experiments ===\n")
    
#     # 1. Quality Analysis (Greedy vs Optimal)
#     quality_results = runner.run_quality_experiments()
#     runner.plot_quality(quality_results)
    
#     # 2. Greedy Big-O Validation
#     greedy_results = runner.run_greedy_runtime_experiments()
#     runner.plot_greedy_big_o(greedy_results)
    
#     # 3. Exhaustive Big-O Validation
#     exhaustive_results = runner.run_exhaustive_runtime_experiments()
#     runner.plot_exhaustive_big_o(exhaustive_results)
    
#     print("\nAll experiments completed! Plots saved in 'plots/' folder.")
    
from src.experiment_runner import ExperimentRunner

runner = ExperimentRunner()
runner.plot_greedy_big_o_from_csv("data/greedy_runtime_results.csv")