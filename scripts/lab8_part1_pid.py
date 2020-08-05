# Nick Zhang 2020
# adapted from crazyflie-lib-python/examples/autonomousSequence.py

# -*- coding: utf-8 -*-
#
#     ||          ____  _ __
#  +------+      / __ )(_) /_______________ _____  ___
#  | 0xBC |     / __  / / __/ ___/ ___/ __ `/_  / / _ \
#  +------+    / /_/ / / /_/ /__/ /  / /_/ / / /_/  __/
#   ||  ||    /_____/_/\__/\___/_/   \__,_/ /___/\___/
#
#  Copyright (C) 2016 Bitcraze AB
#
#  Crazyflie Nano Quadcopter Client
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA  02110-1301, USA.
"""
Simple example that connects to one crazyflie (check the address at the top
and update it to your crazyflie address) and send a sequence of setpoints,
one every 5 seconds.

This example is intended to work with the Loco Positioning System in TWR TOA
mode. It aims at documenting how to set the Crazyflie in position control mode
and how to send setpoints.
"""
import time
import numpy as np

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.log import LogConfig
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.crazyflie.syncLogger import SyncLogger

# Change the sequence according to your setup
#             x    y    z  YAW
sequence = [
    # make sure the x,y coordinate of the first waypoint is 0,0
    (0, 0, 0.4, 0),
    (0.5, 0, 0.4, 0),
    (0.5, 0.5, 0.4, 0),
    (0.5, 0.5, 0.1, 0),
]


def wait_for_position_estimator(scf):
    print('Waiting for estimator to find position...')

    log_config = LogConfig(name='Kalman Variance', period_in_ms=100)
    log_config.add_variable('kalman.varPX', 'float')
    log_config.add_variable('kalman.varPY', 'float')
    log_config.add_variable('kalman.varPZ', 'float')

    var_y_history = [1000] * 10
    var_x_history = [1000] * 10
    var_z_history = [1000] * 10

    threshold = 0.001

    with SyncLogger(scf, log_config) as logger:
        for log_entry in logger:
            data = log_entry[1]

            var_x_history.append(data['kalman.varPX'])
            var_x_history.pop(0)
            var_y_history.append(data['kalman.varPY'])
            var_y_history.pop(0)
            var_z_history.append(data['kalman.varPZ'])
            var_z_history.pop(0)

            min_x = min(var_x_history)
            max_x = max(var_x_history)
            min_y = min(var_y_history)
            max_y = max(var_y_history)
            min_z = min(var_z_history)
            max_z = max(var_z_history)

            # print("{} {} {}".
            #       format(max_x - min_x, max_y - min_y, max_z - min_z))

            if (max_x - min_x) < threshold and (
                    max_y - min_y) < threshold and (
                    max_z - min_z) < threshold:
                break


def reset_estimator(scf):
    cf = scf.cf
    cf.param.set_value('kalman.resetEstimation', '1')
    time.sleep(0.1)
    cf.param.set_value('kalman.resetEstimation', '0')

    wait_for_position_estimator(cf)

# set PID gains
def set_gains(scf):
    # Default gain
    # posCtlPid.xKp: 2.0
    # posCtlPid.xKi: 0.0
    # posCtlPid.xKd: 0.0
    # posCtlPid.yKp: 2.0
    # posCtlPid.yKi: 0.0
    # posCtlPid.yKd: 0.0
    # posCtlPid.zKp: 2.0
    # posCtlPid.zKi: 0.5
    # posCtlPid.zKd: 0.0

    # Modify Position Gains
    scf.cf.param.set_value('posCtlPid.xKp', 2.0)
    scf.cf.param.set_value('posCtlPid.xKd', 0.5)
    scf.cf.param.set_value('posCtlPid.yKp', 2.0)
    scf.cf.param.set_value('posCtlPid.yKd', 0.5)
    scf.cf.param.set_value('posCtlPid.zKp', 2.0)
    scf.cf.param.set_value('posCtlPid.zKd', 0.5)

    # Modify Velocity Gains
    scf.cf.param.set_value('velCtlPid.vxKp', 10.0)
    scf.cf.param.set_value('velCtlPid.vxKi', 1.0)
    scf.cf.param.set_value('velCtlPid.vyKp', 10.0)
    scf.cf.param.set_value('velCtlPid.vyKi', 1.0)
    scf.cf.param.set_value('velCtlPid.vzKp', 15.0)
    scf.cf.param.set_value('velCtlPid.vzKi', 15.0)


log_vec = []
target = (0,0,0)
def position_callback(timestamp, data, logconf):
    global log_vec,target

    t = timestamp
    x = data['kalman.stateX']
    y = data['kalman.stateY']
    z = data['kalman.stateZ']
    print('pos: ({}, {}, {})'.format(x, y, z))
    log_vec.append([t,x,y,z,target[0],target[1],target[2]])


def start_position_logging(scf):
    log_conf = LogConfig(name='Position', period_in_ms=10)
    log_conf.add_variable('kalman.stateX', 'float')
    log_conf.add_variable('kalman.stateY', 'float')
    log_conf.add_variable('kalman.stateZ', 'float')

    scf.cf.log.add_config(log_conf)
    log_conf.data_received_cb.add_callback(position_callback)
    log_conf.start()


def run_sequence(scf, sequence):
    global target
    cf = scf.cf

    # Takeoff gently
    initial_position = sequence[0]
    for y in range(10):
        # vx(forward), vy(left), yawrate(cw viewd from above), z_distance(absolute)
        cf.commander.send_position_setpoint(0, 0, y / 10.0 * initial_position[2], 0)
        target = (0,0,y/25)
        time.sleep(0.1)

    for position in sequence:
        print('Setting position {}'.format(position))
        for i in range(50):
            cf.commander.send_position_setpoint(position[0],
                                                position[1],
                                                position[2],
                                                position[3])
            target = (position[0],position[1],position[2])
            time.sleep(0.1)

    cf.commander.send_stop_setpoint()
    # Make sure that the last packet leaves before the link is closed
    # since the message queue is not flushed before closing
    time.sleep(0.1)


if __name__ == '__main__':
    cflib.crtp.init_drivers(enable_debug_driver=False)

    print('Scanning interfaces for Crazyflies...')
    available = cflib.crtp.scan_interfaces()
    assert len(available) == 1, print('can not find crazyflie, try again')
    print('Crazyflies found.')

    uri = available[0][0]

    with SyncCrazyflie(uri, cf=Crazyflie(rw_cache='./cache')) as scf:
        reset_estimator(scf)
        set_gains(scf)
        start_position_logging(scf)
        run_sequence(scf, sequence)
    np.save('lab8_log',log_vec)
    print("log saved")
