from sys import stdin
import sys
import math
import time as timem
from Motor_Driver import MotorDriver


L = 220 / 2 / 1000
K = 220 / 2 / 1000
B = 45
WHEEL_DIAMETR = 78 / 1000
MAX_SPEED = 2 * math.pi * 175 /  60 
platform = MotorDriver("/dev/ttyAMA0", 115200)


def linear_to_wheel(X_SPEED: float, Y_SPEED: float, M_SPEED: float) -> list:
    global L, K, WHEEL_DIAMETR, B


    alpha = [0 for i in range(4)]
    betta = [0 for i in range(4)]
    Fx = [0 for i in range(4)]
    Fy = [0 for i in range(4)]
    Phi = [0 for i in range(4)]
    Vel = [0 for i in range(4)]
    Ang = [0 for i in range(4)]

    alpha[0] = math.atan2(L, K)
    alpha[1] = math.atan2(L, -K)
    alpha[2] = math.atan2(-L, -K)
    alpha[3] = math.atan2(-L, K)
    betta[0] = math.radians(B)
    betta[1] = math.radians(-B)
    betta[2] = math.radians(B)
    betta[3] = math.radians(-B)

    for i in range(0,4):
        Fx[i] = X_SPEED - math.sqrt(K * K + L * L) * M_SPEED * math.sin(alpha[i] )
        Fy[i] = Y_SPEED + math.sqrt(K * K + L * L) * M_SPEED * math.cos(alpha[i])
        F = math.sqrt(Fx[i] ** 2 + Fy[i] ** 2)
        Phi[i] = math.atan2(Fy[i], Fx[i])
        Vel[i] = F * math.cos(Phi[i]) - F * math.sin(Phi[i]) / math.tan(betta[i])
        Ang[i] = Vel[i] * 2 / WHEEL_DIAMETR
    
    row_speeds = []    
    for i in range(0,4):
        row_speeds.append(float( '{:.4f}'.format(Ang[i]))) 
    # print(row_speeds)
    return row_speeds



def mapping(speeds: list) -> list:
    global MAX_SPEED
    max_speed = max(speeds)
    if max_speed <= MAX_SPEED:
        return speeds
    else:
        for i in range(len(speeds)):
            speeds[i] = speeds[i] * (MAX_SPEED / max_speed)
        return speeds



def coords_to_linear(x: float, y: float, time: float) -> (float, float):
    return x / time / 1000, y / time / 1000



def to_percent(speeds: list):
    global MAX_SPEED
    for i in range(len(speeds)):
        speeds[i] /= MAX_SPEED
        speeds[i] *= 100
    return list(map(int, speeds))

def stop(type: bool):
    global platform
    platform.stop("A", type)
    platform.stop("B", type)
    platform.stop("D", type)
    platform.stop("C", type)

# dela = input()
platform.reverse("A", True, True)
platform.reverse("D", True, True)


def go(x: float, y: float, alpha: float, speed: float):
    global platform, MAX_SPEED
    
    if speed < 0 or speed > 100:
        raise ValueError("Speed must be between 0 and 100 percent")
    
    # Преобразуем скорость в радианы/сек
    max_robot_speed = MAX_SPEED * (speed / 100) * WHEEL_DIAMETR * 1000 / 2
    

    # Вычисляем требуемые линейные скорости
    distance = math.sqrt(x**2 + y**2)  # Евклидово расстояние до точки
    move_time = distance / max_robot_speed if max_robot_speed > 0 else 1  # Время движения
    print(f"move_time:{move_time}")
    # Вычисляем скорости в локальной системе робота
    x_speed = (x / move_time) / 1000
    y_speed = (y / move_time) / 1000
    m_speed = math.radians(alpha) / move_time  # Угловая скорость
    
    # Преобразуем в скорости колес
    wheel_speeds = linear_to_wheel(x_speed, y_speed, m_speed)
    percent_speeds = to_percent(wheel_speeds)
    
    # Применяем ограничение по скорости
    percent_speeds = [s * (speed / 100) for s in percent_speeds]
    
    # Сбрасываем счетчики энкодеров
    platform.resetCount("A")
    platform.resetCount("B")
    platform.resetCount("C")
    platform.resetCount("D")
    
    start_time = timem.time()
    now_time = start_time
    
    kp = 0.1  # Коэффициент ПИД-регулятора
    bar = 5

    while now_time - start_time < move_time:
        now_time = timem.time()
        print(now_time - start_time)
        # Целевые и реальные значения энкодеров
        expected_count = [wheel_speeds[i] * (now_time - start_time) * 0.5 / math.pi * 360 for i in range(4)]
        real_count = [platform.getCount(m) for m in "ABCD"]
        
        # Коррекция скорости
        correction = [(expected_count[i] - real_count[i]) * kp / MAX_SPEED * 100 for i in range(4)]
        correction = [max(min(c, bar), -bar) for c in correction]
        print(real_count, correction)
        platform.start("ABCD", [percent_speeds[i] + correction[i] for i in range(4)])
        
        timem.sleep(0.01)
    
    stop(True)
    
go(100,0,0,50)