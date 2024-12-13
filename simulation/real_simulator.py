# project/simulation/real_simulator.py
import csv
import random
import time
import threading
from typing import List

def run_real_simulation(bridge_instance, direction_list: List[str], threaded: bool, output_file: str, arrival_span: float):
    """
    Запускает реальную симуляцию с измерением фактического времени.
    - arrival_span: максимальное случайное время задержки перед началом движения каждой машины
    - threaded: если True, для каждой машины создаётся поток
    """
    results = []
    num_cars = len(direction_list)

    # Генерируем случайные задержки перед появлением машин
    arrival_delays = [random.uniform(0, arrival_span) for _ in direction_list]
    cars = list(zip(range(1, num_cars+1), direction_list, arrival_delays))

    # Для многопоточного режима мы хотим запустить каждую машину в отдельном потоке
    if threaded:
        lock_results = threading.Lock()  # чтобы безопасно записывать результаты из потоков

        def car_thread(car_id: int, direction: str, delay: float):
            # Ждём "прихода" машины
            time.sleep(delay)
            arrival_time = time.time()

            # Заезд на мост (блокирующий вызов enter)
            enter_time = bridge_instance.enter(direction, arrival_time)
            wait_time = enter_time - arrival_time

            # Выезд с моста
            leave_time = bridge_instance.leave(enter_time)
            crossing_time = leave_time - enter_time

            with lock_results:
                results.append((car_id, direction, wait_time, crossing_time, arrival_time))

        threads = []
        for (car_id, direction, delay) in cars:
            t = threading.Thread(target=car_thread, args=(car_id, direction, delay))
            threads.append(t)

        for t in threads:
            t.start()
        for t in threads:
            t.join()

    else:
        # Последовательно
        for (car_id, direction, delay) in cars:
            time.sleep(delay)
            arrival_time = time.time()

            enter_time = bridge_instance.enter(direction, arrival_time)
            wait_time = enter_time - arrival_time

            leave_time = bridge_instance.leave(enter_time)
            crossing_time = leave_time - enter_time

            results.append((car_id, direction, wait_time, crossing_time, arrival_time))

    # Сохраняем результаты
    with open(output_file, "w", newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["CarID", "Direction", "WaitingTime", "CrossingTime", "ArrivalTime"])
        for r in results:
            writer.writerow(r)

    print(f"REAL simulation results saved to {output_file}")
