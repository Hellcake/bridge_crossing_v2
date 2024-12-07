# project/simulation/simulator.py
import csv
import random
from typing import List


def run_simulation(bridge_instance, direction_list: List[str], threaded: bool, output_file: str, arrival_span: float):
    results = []
    arrival_times = [random.uniform(0, arrival_span) for _ in direction_list]
    cars = list(zip(range(1, len(direction_list)+1), direction_list, arrival_times))
    cars.sort(key=lambda x: x[2])

    if threaded:
        import threading
        def car_thread(car_id: int, direction: str, arrival_time: float):
            enter_time = bridge_instance.enter(direction, arrival_time)
            wait_time = enter_time - arrival_time
            leave_time = bridge_instance.leave(enter_time)
            crossing_time = leave_time - enter_time
            results.append((car_id, direction, wait_time, crossing_time, arrival_time))

        threads = []
        for (car_id, direction, a_time) in cars:
            t = threading.Thread(target=car_thread, args=(car_id, direction, a_time))
            threads.append(t)

        for t in threads:
            t.start()
        for t in threads:
            t.join()
    else:
        for (car_id, direction, a_time) in cars:
            enter_time = bridge_instance.enter(direction, a_time)
            wait_time = enter_time - a_time
            leave_time = bridge_instance.leave(enter_time)
            crossing_time = leave_time - enter_time
            results.append((car_id, direction, wait_time, crossing_time, a_time))

    # Сохраняем результаты
    with open(output_file, "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["CarID", "Direction", "WaitingTime", "CrossingTime", "ArrivalTime"])
        for r in results:
            writer.writerow(r)

    print(f"Результаты сохранены в {output_file}")
