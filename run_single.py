# run_single.py
from bridge.single_threaded import SingleThreadedBridge
from simulation.simulator import run_simulation

if __name__ == "__main__":
    # Допустим, 100 машин и интервал прибытия 10 секунд
    directions = ["left", "right"] * 10000
    bridge = SingleThreadedBridge()
    run_simulation(bridge_instance=bridge,
                   direction_list=directions,
                   threaded=False,
                   output_file="single_threaded_results.csv",
                   arrival_span=10.0)
