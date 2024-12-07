import os
import csv
import matplotlib.pyplot as plt
import random

from bridge.single_threaded import SingleThreadedBridge
from bridge.multi_threaded import MultiThreadedBridge
from simulation.simulator import run_simulation

def load_results(filename):
    cars = []
    with open(filename, "r", newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            car_id = int(row["CarID"])
            direction = row["Direction"]
            wait = float(row["WaitingTime"])
            cross = float(row["CrossingTime"])
            # arrival_time = float(row["ArrivalTime"]) если нужно
            cars.append((car_id, direction, wait, cross))
    return cars

def compute_stats(cars):
    waits = [c[2] for c in cars]
    avg_wait = sum(waits)/len(waits) if waits else 0
    max_wait = max(waits) if waits else 0
    return avg_wait, max_wait

if __name__ == "__main__":
    # Примерный набор количеств машин
    num_cars_list = [100, 500, 1000, 2000, 5000, 10000]
    arrival_span = 10.0

    # Вероятность направления: пусть равномерно
    # Если хотим рандомный выбор направления, просто в самом цикле генерируем списки направлений случайно.
    # Или можно задать bias, например 50/50:
    p_left = 0.5

    single_avg_waits = []
    single_max_waits = []
    multi_avg_waits = []
    multi_max_waits = []

    for n in num_cars_list:
        # Генерируем случайные направления
        directions = [("left" if random.random() < p_left else "right") for _ in range(n)]
        
        # Однопоточный мост
        single_file = "single_temp.csv"
        bridge_single = SingleThreadedBridge()
        run_simulation(bridge_instance=bridge_single,
                       direction_list=directions,
                       threaded=False,
                       output_file=single_file,
                       arrival_span=arrival_span)
        single_cars = load_results(single_file)
        s_avg, s_max = compute_stats(single_cars)
        single_avg_waits.append(s_avg)
        single_max_waits.append(s_max)

        # Многопоточный мост
        multi_file = "multi_temp.csv"
        bridge_multi = MultiThreadedBridge()
        run_simulation(bridge_instance=bridge_multi,
                       direction_list=directions,
                       threaded=True,
                       output_file=multi_file,
                       arrival_span=arrival_span)
        multi_cars = load_results(multi_file)
        m_avg, m_max = compute_stats(multi_cars)
        multi_avg_waits.append(m_avg)
        multi_max_waits.append(m_max)

        os.remove(single_file)
        os.remove(multi_file)

        print(f"For {n} cars:")
        print(f"  Single-threaded: Avg wait = {s_avg:.4f}, Max wait = {s_max:.4f}")
        print(f"  Multi-threaded:  Avg wait = {m_avg:.4f}, Max wait = {m_max:.4f}")

    # Строим график среднего времени ожидания
    plt.figure(figsize=(10,6))
    plt.plot(num_cars_list, single_avg_waits, marker='o', label="Single-threaded Avg")
    plt.plot(num_cars_list, multi_avg_waits, marker='o', label="Multi-threaded Avg")
    plt.xlabel("Number of cars")
    plt.ylabel("Average waiting time (s)")
    plt.title("Scaling of average waiting times with number of cars")
    plt.legend()
    plt.grid(True)
    plt.savefig("scalability_comparison_avg.png")
    plt.show()

    # Строим график максимального времени ожидания
    plt.figure(figsize=(10,6))
    plt.plot(num_cars_list, single_max_waits, marker='o', label="Single-threaded Max Wait")
    plt.plot(num_cars_list, multi_max_waits, marker='o', label="Multi-threaded Max Wait")
    plt.xlabel("Number of cars")
    plt.ylabel("Maximum waiting time (s)")
    plt.title("Scaling of maximum waiting times with number of cars")
    plt.legend()
    plt.grid(True)
    plt.savefig("scalability_comparison_max.png")
    plt.show()
