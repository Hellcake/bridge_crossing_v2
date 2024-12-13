# project/real_vs_logic.py
import os
import csv
import matplotlib.pyplot as plt
import random
import time

# Логические классы мостов
from bridge.single_threaded import SingleThreadedBridge
from bridge.multi_threaded import MultiThreadedBridge

# Реальные классы мостов
from bridge.real_single_threaded import RealSingleThreadedBridge
from bridge.real_multi_threaded import RealMultiThreadedBridge

# Функции симуляции
from simulation.simulator import run_simulation           # логическая симуляция
from simulation.real_simulator import run_real_simulation # реальная симуляция

def load_results(filename):
    cars = []
    with open(filename, "r", newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            car_id = int(row["CarID"])
            direction = row["Direction"]
            wait = float(row["WaitingTime"])
            cross = float(row["CrossingTime"])
            arrival_time = float(row["ArrivalTime"])
            cars.append((car_id, direction, wait, cross, arrival_time))
    return cars

def compute_wait_stats(cars):
    """
    Среднее и максимальное время ожидания.
    """
    waits = [c[2] for c in cars]  # c[2] = wait_time
    avg_wait = sum(waits)/len(waits) if waits else 0
    max_wait = max(waits) if waits else 0
    return avg_wait, max_wait

def compute_logic_total_time(cars):
    """
    'Логическое' общее время = (finish_time последней машины) - (минимальное arrival_time).
    finish_time = arrival_time + waiting_time + crossing_time.
    """
    if not cars:
        return 0
    min_arrival = min(c[4] for c in cars)  # c[4] = arrival_time
    finish_times = [c[4] + c[2] + c[3] for c in cars]  # arrival_time + wait_time + crossing_time
    max_finish = max(finish_times)
    total_time = max_finish - min_arrival
    return total_time

if __name__ == "__main__":
    # Кол-ва машин для тестов
    num_cars_list = [5, 10, 50, 100]
    arrival_span = 2.0  # Для real-модели, чтобы не слишком затягивать

    # Вероятность направления - 50/50
    p_left = 0.5

    # Храним результаты по следующим метрикам:
    #   logic_single_time, logic_multi_time : "логическое" общее время
    #   real_single_time, real_multi_time   : реальное (физическое) общее время
    logic_single_time = []
    logic_multi_time  = []
    real_single_time  = []
    real_multi_time   = []

    # (Опционально) можно продолжать собирать средние/макс ожидания, чтобы смотреть на тенденции
    logic_single_avg_wait = []
    logic_multi_avg_wait  = []
    real_single_avg_wait  = []
    real_multi_avg_wait   = []

    for n in num_cars_list:
        directions = [("left" if random.random() < p_left else "right") for _ in range(n)]
        
        ### ЛОГИЧЕСКАЯ ОДНОПОТОЧНАЯ ###
        single_file = "logic_single_temp.csv"
        bridge_single = SingleThreadedBridge()
        run_simulation(
            bridge_instance=bridge_single,
            direction_list=directions,
            threaded=False,
            output_file=single_file,
            arrival_span=10.0  # "логическое" arrival_span
        )
        single_cars = load_results(single_file)
        os.remove(single_file)

        logic_single_tt = compute_logic_total_time(single_cars)  # логическое общее время
        logic_single_time.append(logic_single_tt)

        s_avg, _ = compute_wait_stats(single_cars)
        logic_single_avg_wait.append(s_avg)

        ### ЛОГИЧЕСКАЯ МНОГОПОТОЧНАЯ ###
        multi_file = "logic_multi_temp.csv"
        bridge_multi = MultiThreadedBridge()
        run_simulation(
            bridge_instance=bridge_multi,
            direction_list=directions,
            threaded=True,
            output_file=multi_file,
            arrival_span=10.0
        )
        multi_cars = load_results(multi_file)
        os.remove(multi_file)

        logic_multi_tt = compute_logic_total_time(multi_cars)
        logic_multi_time.append(logic_multi_tt)

        m_avg, _ = compute_wait_stats(multi_cars)
        logic_multi_avg_wait.append(m_avg)

        ### РЕАЛЬНАЯ ОДНОПОТОЧНАЯ ###
        real_single_file = "real_single_temp.csv"
        real_single_bridge = RealSingleThreadedBridge()
        start_time = time.time()
        # Здесь threaded=False, чтобы САМА симуляция шла в одном потоке
        run_real_simulation(
            bridge_instance=real_single_bridge,
            direction_list=directions,
            threaded=False,
            output_file=real_single_file,
            arrival_span=arrival_span
        )
        end_time = time.time()
        real_single_total = end_time - start_time  # реальное время выполнения всей симуляции
        real_single_time.append(real_single_total)

        real_single_cars = load_results(real_single_file)
        os.remove(real_single_file)

        rs_avg, _ = compute_wait_stats(real_single_cars)
        real_single_avg_wait.append(rs_avg)

        ### РЕАЛЬНАЯ МНОГОПОТОЧНАЯ ###
        real_multi_file = "real_multi_temp.csv"
        real_multi_bridge = RealMultiThreadedBridge()
        start_time = time.time()
        # threaded=True, чтобы многопоточность реально включалась
        run_real_simulation(
            bridge_instance=real_multi_bridge,
            direction_list=directions,
            threaded=True,
            output_file=real_multi_file,
            arrival_span=arrival_span
        )
        end_time = time.time()
        real_multi_total = end_time - start_time
        real_multi_time.append(real_multi_total)

        real_multi_cars = load_results(real_multi_file)
        os.remove(real_multi_file)

        rm_avg, _ = compute_wait_stats(real_multi_cars)
        real_multi_avg_wait.append(rm_avg)

        print(f"\n=== For {n} cars ===")
        print(f"Logic Single:  total_time = {logic_single_tt:.2f},   avg_wait = {s_avg:.2f}")
        print(f"Logic Multi:   total_time = {logic_multi_tt:.2f},   avg_wait = {m_avg:.2f}")
        print(f"Real Single:   total_time = {real_single_total:.2f}, avg_wait = {rs_avg:.4f}")
        print(f"Real Multi:    total_time = {real_multi_total:.2f},  avg_wait = {rm_avg:.4f}")

    ########## ПОСТРОИМ ГРАФИКИ ##########

    # 1) Сравнение "логическое время симуляции" vs "реальное общее время" – Single
    plt.figure(figsize=(10,6))
    plt.plot(num_cars_list, logic_single_time, marker='o', label="Logic Single (Total Logic Time)")
    plt.plot(num_cars_list, real_single_time, marker='o', label="Real Single (Total Real Time)")
    plt.xlabel("Number of cars")
    plt.ylabel("Simulation total time (seconds)")
    plt.title("Single-threaded: Logic vs Real (trend comparison)")
    plt.legend()
    plt.grid(True)
    plt.savefig("compare_single_total_time.png")
    plt.show()

    # 2) Сравнение "логическое время" vs "реальное время" – Multi
    plt.figure(figsize=(10,6))
    plt.plot(num_cars_list, logic_multi_time, marker='o', label="Logic Multi (Total Logic Time)")
    plt.plot(num_cars_list, real_multi_time, marker='o', label="Real Multi (Total Real Time)")
    plt.xlabel("Number of cars")
    plt.ylabel("Simulation total time (seconds)")
    plt.title("Multi-threaded: Logic vs Real (trend comparison)")
    plt.legend()
    plt.grid(True)
    plt.savefig("compare_multi_total_time.png")
    plt.show()

    # 3) Сравнение real_single vs real_multi (общее реальное время)
    plt.figure(figsize=(10,6))
    plt.plot(num_cars_list, real_single_time, marker='o', label="Real Single (Total Execution Time)")
    plt.plot(num_cars_list, real_multi_time, marker='o', label="Real Multi (Total Execution Time)")
    plt.xlabel("Number of cars")
    plt.ylabel("Total real execution time (seconds)")
    plt.title("Real Single vs Real Multi: total execution time")
    plt.legend()
    plt.grid(True)
    plt.savefig("real_single_vs_multi.png")
    plt.show()

    # 4) (Опционально) Сравнение тенденций среднего ожидания (Logic vs Real).
    plt.figure(figsize=(10,6))
    plt.plot(num_cars_list, logic_single_avg_wait, marker='o', label="Logic Single AvgWait")
    plt.plot(num_cars_list, logic_multi_avg_wait, marker='o', label="Logic Multi AvgWait")
    plt.plot(num_cars_list, real_single_avg_wait, marker='o', label="Real Single AvgWait")
    plt.plot(num_cars_list, real_multi_avg_wait, marker='o', label="Real Multi AvgWait")
    plt.xlabel("Number of cars")
    plt.ylabel("Average waiting time (s)")
    plt.title("Avg waiting time comparison (Logic vs Real)")
    plt.legend()
    plt.grid(True)
    plt.savefig("avg_wait_comparison.png")
    plt.show()
