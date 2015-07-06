'''
Created on Nov 5, 2014

@author: alexander
'''

import os
import rrdtool


def draw_all_rrd(dir_root, dir_doc, start_time, end_time):
    """
    Creates graph files in .png format in /images subdirectory and aggregated
values.
    :param dir_root: string. Directory that contains cluster directory with rrd
files. The common value is '/var/lib/ganglia/rrds/cluster/'.
    :param dir_doc: string. Directory where all graphs and aggregated values
will be stored. For example,
'/home/alexander/Documents/sber/local/mk-sber-docs'
    :param start_time: string. The start time in epoch.
    :param end_time: string. The end time in epoch.
    """
    metrics_dict = {"load_one": "Average over period",
                    "cpu_intr": "%",
                    "load_five": "Average over period",
                    "cpu_sintr": "%",
                    "load_fifteen": "Average over period",
                    "cpu_idle": "%",
                    "cpu_aidle": "%",
                    "cpu_nice": "%",
                    "cpu_user": "%",
                    "cpu_system": "%",
                    "cpu_wio": "%",
                    "cpu_num": "Count",
                    "cpu_speed": "Mhz",
                    "part_max_used": "%",
                    "disk_total": "Gb",
                    "disk_free": "Gb",
                    "mem_total": "Kb",
                    "proc_run": "Count",
                    "mem_cached": "Kb",
                    "swap_total": "Kb",
                    "mem_free": "Kb",
                    "mem_buffers": "Kb",
                    "mem_shared": "Kb",
                    "proc_total": "Count",
                    "swap_free": "Kb",
                    "pkts_out": "Packets/seconds",
                    "pkts_in": "Packets/seconds",
                    "bytes_in": "Bytes/second",
                    "bytes_out": "Bytes/second",
                    "boottime": "Timestamp",
                    "wildfly8_Memory_Heap_init": "bytes",
                    "wildfly8_Memory_Heap_committed": "bytes",
                    "wildfly8_Memory_Heap_used": "bytes",
                    "wildfly8_Memory_Heap_max": "bytes",
                    "wildfly8_Memory_NonHeap_init": "bytes",
                    "wildfly8_Memory_NonHeap_committed": "bytes",
                    "wildfly8_Memory_NonHeap_used": "bytes",
                    "wildfly8_Memory_NonHeap_max": "bytes",
                    "wildfly8_OS_ProcessCpuTime": "ns",
                    "wildfly8_Threading_DaemonThreadCount": "Count",
                    "wildfly8_Threading_ThreadCount": "Count",
                    }

    dir_list = os.listdir(dir_root)
    # Put path of every node to list
    filtered = []
    for v in dir_list:
        if not v.startswith('_'):
            filtered.append(dir_root + v)

    for node_name in filtered:
        if not os.path.exists(
            dir_doc + "/" + node_name.split('/')[-1] +
                "/images"):
            os.makedirs(dir_doc + "/" + node_name.split('/')[-1] + "/images")

        for file_name in os.listdir(node_name):
            # Get an average, max, min values and image respectively for
            # particular metric

            common_args = [
                dir_doc + "/" + node_name.split('/')[-1] + "/images/" +
                file_name.split('.')[0] + ".png",
                '--width', '600',
                '--height', '200',
                "--vertical-label",
                metrics_dict[os.path.splitext(file_name)[0]],
                '--start', start_time.split('.')[0],
                '--end', end_time.split('.')[0],
                '-F',
                '--title', file_name,
            ]

            new_node_data_file = open(
                dir_doc + "/" + node_name.split('/')[-1] +
                "/" + file_name.split('.')[0] + "-log", "w")

            tail = [
                'DEF:sum=' + node_name + "/" + file_name + ':sum:AVERAGE',
                'VDEF:vm=sum,AVERAGE',
                'PRINT:vm:%lf',
            ]
            result_to_write = rrdtool.graph(common_args + tail)[2][0]
            new_node_data_file.write(
                "AVERAGE: " + result_to_write + ' ' +
                metrics_dict[os.path.splitext(file_name)[0]] + '\n')

            tail = [
                'DEF:sum=' + node_name + "/" + file_name + ':sum:MIN',
                'VDEF:vm=sum,MINIMUM',
                'PRINT:vm:%lf',
            ]
            result_to_write = rrdtool.graph(common_args + tail)[2][0]
            new_node_data_file.write(
                "MIN: " + result_to_write + ' ' +
                metrics_dict[os.path.splitext(file_name)[0]] + '\n')

            tail = [
                'DEF:sum=' + node_name + "/" + file_name + ':sum:MAX',
                'VDEF:vm=sum,MAXIMUM',
                'PRINT:vm:%lf',
            ]
            result_to_write = rrdtool.graph(common_args + tail)[2][0]
            new_node_data_file.write(
                "MAX: " + result_to_write + ' ' +
                metrics_dict[os.path.splitext(file_name)[0]] + '\n')

            new_node_data_file.close()

            tail = [
                'DEF:sum=' + node_name + "/" + file_name + ':sum:AVERAGE',
                'LINE2:sum#FF0000',
            ]
            rrdtool.graph(common_args + tail)
