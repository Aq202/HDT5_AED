import simpy as sp
import random
import numpy as np
import pyperclip


class OperativeSystem:

    def __init__(self, env, ramCapacity=100, tasksExecutionCapacity=3, cpuNumber=1):

        self.env = env
        self.ram = sp.Container(env, init=ramCapacity, capacity=ramCapacity)
        self.cpu = sp.Resource(env, capacity=cpuNumber)
        self.IO_operations = sp.Resource(env, capacity=1)
        self.tasksExecutionCapacity = tasksExecutionCapacity
        self.executionsRecord = []

        self.resume = self.env.event()

    def newProcess(self, memoryWeight, pendingTasks, arrivalDelay=0):

        yield self.env.timeout(arrivalDelay)
        startTime = self.env.now

        print(
            f"[NEW] Esperando asignacion de memoria, en t={self.env.now}, cantidad de memoria requerida={memoryWeight}, memoria disponible={self.ram.level}")

        yield self.ram.get(memoryWeight)

        while pendingTasks > 0:

            print(
                f"[READY] Proceso en cola , t={self.env.now}, instrucciones pendientes={pendingTasks}")

            with self.cpu.request() as cpu:
                yield cpu

                pendingTasks = pendingTasks - self.tasksExecutionCapacity
                pendingTasks = pendingTasks if pendingTasks > 0 else 0
                yield self.env.timeout(1)  # ciclo de reloj

                print(
                    f"[RUNNING] Proceso ejecutado en t={self.env.now}, memoria={memoryWeight}, instrucciones pendientes={pendingTasks}")

            if pendingTasks > 0:

                if random.randint(1, 2) == 1:
                    # operacionesde Input/Output
                    print(
                        f"[WAITING] Proceso en cola para realizar operaciones I/O, en t={self.env.now}")
                    with self.IO_operations.request() as IO:
                        yield IO
                        yield self.env.timeout(1)

        # liberar memoria
        self.ram.put(memoryWeight)

        endTime = self.env.now
        executionTime = endTime - startTime
        self.executionsRecord.append(executionTime)

        print(
            f"[TERMINATED] Proceso finalizado en t={endTime}, tiempo de ejecucion={executionTime}, memoria liberada={memoryWeight}, memoria disponible={self.ram.level}")


if __name__ == "__main__":

    random.seed(2002)

    NUMBER_OF_PROCESSES = 25
    INTERVAL = 1
    RAM = 100
    TASK_EXECUTION_CAPACITY = 3
    CPU_NUMBER = 1

    env = sp.Environment()
    OS = OperativeSystem(
        env, ramCapacity=RAM, tasksExecutionCapacity=TASK_EXECUTION_CAPACITY, cpuNumber=CPU_NUMBER)

    for i in range(NUMBER_OF_PROCESSES):
        executionStart = random.expovariate(1.0 / INTERVAL)
        env.process(OS.newProcess(
            random.randint(1, 50), random.randint(1, 10), arrivalDelay=executionStart))

        print(f"exec start {executionStart}")
    env.run()

    print("\n----------SIMULACION FINALIZADA----------\n")
    mean = np.mean(OS.executionsRecord)
    desv = np.std(OS.executionsRecord)

    pyperclip.copy(f"{mean}\t{desv}")

    print(f"Tiempo promedio de ejecucion = {mean}")
    print(f"Desviacion estandar = {desv}")
