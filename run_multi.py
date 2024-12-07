# run_multi.py
from bridge.multi_threaded import MultiThreadedBridge
from simulation.simulator import run_simulation

if __name__ == "__main__":
    directions = ["left", "right"] * 10000
    bridge = MultiThreadedBridge()
    run_simulation(bridge_instance=bridge,
                   direction_list=directions,
                   threaded=True,
                   output_file="multi_threaded_results.csv",
                   arrival_span=10.0)
