import csv
import matplotlib.pyplot as plt

def load_results(filename):
    cars = []
    with open(filename, "r", newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            car_id = int(row["CarID"])
            direction = row["Direction"]
            wait = float(row["WaitingTime"])
            cross = float(row["CrossingTime"])
            cars.append((car_id, direction, wait, cross))
    return cars

def compute_stats(cars):
    waits = [c[2] for c in cars]
    avg_wait = sum(waits)/len(waits) if waits else 0
    max_wait = max(waits) if waits else 0
    crosses = [c[3] for c in cars]
    avg_cross = sum(crosses)/len(crosses) if crosses else 0
    return avg_wait, max_wait, avg_cross

def compare_results(single_file="single_threaded_results.csv", multi_file="multi_threaded_results.csv"):
    single_cars = load_results(single_file)
    multi_cars = load_results(multi_file)

    s_avg_wait, s_max_wait, s_avg_cross = compute_stats(single_cars)
    m_avg_wait, m_max_wait, m_avg_cross = compute_stats(multi_cars)

    print("Single-threaded:")
    print(f"  Avg wait: {s_avg_wait:.4f} s, Max wait: {s_max_wait:.4f} s, Avg cross: {s_avg_cross:.4f} s")
    print("Multi-threaded:")
    print(f"  Avg wait: {m_avg_wait:.4f} s, Max wait: {m_max_wait:.4f} s, Avg cross: {m_avg_cross:.4f} s")

    labels = ['Avg Waiting', 'Max Waiting', 'Avg Crossing']
    single_vals = [s_avg_wait, s_max_wait, s_avg_cross]
    multi_vals = [m_avg_wait, m_max_wait, m_avg_cross]

    x = range(len(labels))
    plt.figure(figsize=(10, 6))
    plt.bar([i - 0.2 for i in x], single_vals, width=0.4, label="Single-threaded")
    plt.bar([i + 0.2 for i in x], multi_vals, width=0.4, label="Multi-threaded")
    plt.xticks(range(len(labels)), labels)
    plt.ylabel("Time (s)")
    plt.title("Comparison of Single-threaded vs Multi-threaded Simulation")
    plt.legend()
    plt.savefig("comparison_chart.png")
    plt.show()

if __name__ == "__main__":
    compare_results()
