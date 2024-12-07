# bridge_crossing_v2
## 1. Введение

В данном проекте рассматривается задача моделирования прохождения автомобилей по однополосному мосту с двух сторон, при условии, что в каждый момент времени мост может быть занят автомобилями только одного направления. Цель исследования – разработать и сравнить однопоточную и многопоточную реализации данной задачи, а также проанализировать влияние алгоритмов переключения направления движения на время ожидания автомобилей.

Для достижения цели были поставлены следующие задачи:  
- Разработать модель, в которой автомобили подъезжают к мосту в различные моменты времени и с разных сторон.  
- Реализовать однопоточную версию решения, где все автомобили обрабатываются последовательно.  
- Разработать многопоточную версию, в которой каждый автомобиль представлен отдельным потоком, а синхронизация осуществляется при помощи механизма блокировок и условных переменных.  
- Ввести различные стратегии (алгоритмы) переключения приоритетного направления (от простого варианта до «batching»), чтобы минимизировать суммарное и среднее время ожидания автомобилей.  
- Сравнить результаты однопоточной и многопоточной реализаций, исследовать масштабируемость решения при увеличении числа потоков, а также влияние расстановки приоритетов на результаты.

## 2. Подробное описание задачи

**Суть задачи:**  
Имеется однополосный мост, по которому могут двигаться автомобили в двух противоположных направлениях. В каждый момент времени мост может пропускать либо поток машин, едущих слева направо, либо поток машин, едущих справа налево, но не одновременно оба. Автомобили прибывают к мосту в случайные моменты времени и со случайно заданными направлениями.

**Основные аспекты:**  
- Каждая машина имеет время прибытия к мосту (случайное, в заданном интервале).  
- Время проезда по мосту для одной машины фиксировано (1 секунда логического времени).  
- Если машина не может заехать на мост немедленно из-за приоритета другого направления или занятого моста, она ждёт. Время ожидания – ключевой показатель эффективности алгоритма.  
- Необходимо управлять приоритетом: когда пропускать машины с одной стороны, когда переключаться на другую, чтобы минимизировать общее время ожидания и сбалансировать очереди.

## 3. Описание базового алгоритма (многопоточная реализация)

**Базовая многопоточная модель:**  
- Каждая машина представлена отдельным потоком.
- Для управления доступом к мосту используется общий монитор с `Lock` и `Condition` переменными.
- В простейшем варианте алгоритма, если мост в данный момент обслуживает машины «слева направо», то машины «справа налево» ждут, пока все машины текущего направления не закончат движение. Затем мост «переключается» на другое направление.
- Во время ожидания потоки машин блокируются на условных переменных и пробуждаются, когда меняется приоритет или освобождается мост.

**Модификация алгоритма (batching):**  
Вместо полного исчерпания машин одного направления вводим «партии» (batch) – по несколько машин подряд. Пропустив определённое количество машин, алгоритм может принудительно переключить направление, если это сократит общее ожидание.

## 4. Описание основных процедур и частей программы (многопоточность)

Структура проекта:  
```
project/
    bridge/
        base.py             # Интерфейс моста
        single_threaded.py  # Однопоточная реализация моста
        multi_threaded.py   # Многопоточная реализация с batching
    simulation/
        simulator.py         # Логика запуска симуляций, генерация машин, сбор статистики
    compare/
        compare.py           # Скрипт для сравнения результатов (CSV) и построения графиков
    run_single.py            # Пример запуска однопоточной симуляции
    run_multi.py             # Пример запуска многопоточной симуляции
    scalability_test.py      # Скрипт для экспериментов с разными числами машин
    README.md                # Описание проекта
    requirements.txt
```

**Ключевые процедуры:**

- `enter(direction, arrival_time)`: Поток (машина) вызывает этот метод, чтобы запросить доступ к мосту. Если условия для въезда не выполнены (мост занят или направление не в приоритете), поток блокируется на `condition.wait()`.
  
- `leave(enter_time)`: Машина, проехав мост, освобождает его. Если мост опустел, алгоритм принимает решение о переключении направления или продолжении в том же.
  
**Пример кода (фрагмент из многопоточной реализации)**:

```python
# Упрощенный фрагмент (из multi_threaded.py)
with self.condition:
    if (self.current_direction is None or self.current_direction == direction) and условие_партизации:
        # Машина может въехать
        self.current_direction = direction
        self.on_bridge += 1
        enter_time = max(arrival_time, self.next_available_time(direction))
        return enter_time
    else:
        # Машина ждёт
        self.waiting_for(direction) += 1
        self.condition.wait()
        self.waiting_for(direction) -= 1
```

## 5. Результаты работы приложения. Сравнение многопоточного и однопоточного вариантов

При запуске симуляций результаты сохраняются в CSV-файлы, содержащие для каждой машины:

- Время прибытия
- Время ожидания
- Время проезда (всегда 1 секунда)
- Направление движения

Сравнение показывает, что:  
- В однопоточной модели среднее время ожидания масштабируется примерно линейно с ростом количества машин.  
- Многопоточная модель при использовании простого алгоритма часто даёт схожий (хотя и чуть меньше) рост времени ожидания.  
- При использовании политики batch-переключений многопоточный вариант способен улучшить среднее ожидание в отдельных режимах, делая распределение более сбалансированным. Однако при очень больших количествах машин фундаментальное ограничение (один автомобиль за раз) всё равно приводит к примерно линейному росту ожидания.

## 6. Анализ результатов работы приложения

- **Масштабирование (увеличение числа потоков)**: При малых масштабах (сотни машин) преимущества «умной» многопоточной логики заметны в снижении среднего времени ожидания. При больших масштабах (тысячи и десятки тысяч машин) наблюдается общее увеличение времени ожидания для обеих реализаций, хотя многопоточность с batching помогает незначительно снизить коэффициент роста.

- **Разные конфигурации и архитектуры**: Многопоточность может дать некоторый выигрыш на системах с большим количеством ядер, но с ростом числа машин логический характер времени нивелирует реальные системные различия, так как мы не используем реальные задержки.

- **Влияние приоритетов**: Изменяя стратегию переключения направления (в том числе batch_size), можно добиться более равномерного распределения ожидания между сторонами. Чем более «сбалансирован» алгоритм, тем меньше максимальные времена ожидания отдельных машин.

## 7. Выводы

В ходе работы были рассмотрены различные подходы к управлению проездом машин через однополосный мост. Однопоточная и многопоточная реализации протестированы и сравнены. Результаты показывают, что:

- Однопоточная реализация даёт простой и предсказуемый результат с линейным ростом времени ожидания.
- Многопоточная реализация, даже без использования реальных задержек, не способна кардинально изменить характер зависимости, так как пропускная способность моста остаётся ограниченной.
- Однако внедрение адаптивного алгоритма чередования направлений (batching) позволяет частично снизить среднее время ожидания и сделать систему более «справедливой» для обеих сторон.
- При больших масштабах число потоков и сложность алгоритмов не могут преодолеть фундаментальное ограничение пропускной способности.
- Результаты и код позволяют в дальнейшем тестировать более сложные эвристики переключения направления, изменять распределение прибытий и исследовать другие метрики эффективности.

Таким образом, поставленная цель достигнута: разработана модель, реализованы и сравнены однопоточная и многопоточная версии, проведено исследование масштабируемости и влияния различных стратегий переключения приоритета, и сделаны выводы о характере зависимости времени ожидания от числа машин.
