from sys import stdin
import sys
import math
import time as timem
from Motor_Driver import MotorDriver


L = 220 / 2 / 1000
K = 235 / 2 / 1000
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

dela = input()
platform.reverse("A", True, True)
platform.reverse("D", True, True)

def go(x, y, ang, time):
    x_speed, y_speed = coords_to_linear(x, y, time)
    m_speed = math.radians(ang) / time 
    wheel_speeds = linear_to_wheel(x_speed, y_speed, m_speed)
    percent_speeds = to_percent(wheel_speeds)

    platform.start("ABCD", percent_speeds)
    
    timem.sleep(time)
    stop(True)
    
go(1000, 0, 0, 2)
go(0, 1000, 0, 2)
go(-1000, 0, 0, 2)
go(0, -1000, 0, 2)

while True:
    stop(True)
    x = int(input())
    y = int(input())
    ang = int(input())
    time = float(input())

    x_speed, y_speed = coords_to_linear(x, y, time)
    m_speed = math.radians(ang) / time 
    wheel_speeds = linear_to_wheel(x_speed, y_speed, m_speed)
    percent_speeds = to_percent(wheel_speeds)

    platform.start("ABCD", percent_speeds)
    
    timem.sleep(time)
    stop(True)
    print("OK")