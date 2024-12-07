from bridge.multi_threaded import MultiThreadedBridge
from bridge.single_threaded import SingleThreadedBridge
from simulation.simulator import run_simulation

if __name__ == "__main__":
    directions = ["left", "right"] * 5000  # 10 000 машин
    bridge_single = SingleThreadedBridge()
    run_simulation(bridge_instance=bridge_single,
                   direction_list=directions,
                   threaded=False,
                   output_file="logic_single_results.csv",
                   arrival_span=10.0)

    bridge_multi = MultiThreadedBridge()
    run_simulation(bridge_instance=bridge_multi,
                   direction_list=directions,
                   threaded=True,
                   output_file="logic_multi_results.csv",
                   arrival_span=10.0)
