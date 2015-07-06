'''
Created on Nov 12, 2014

@author: alexander
'''

import os
import rrdtool
from rrdtool import update as rrd_update
from logParser import LogParser


def create_rrd(dir_doc, start_time, client_number):
    """
    Creates rrd files for storing information about clients.
    :param dir_doc: String. Path to the directory where rrd will be placed
    :param start_time: String. The very first timestamp in the new
    :param clien_number: int. Number of clients. Affects on what files will be
read
    :return: String. Path to the new created rrd file.
    """
    tmp_database_name = dir_doc + "/tmp_database.rrd"
    arg_string = [tmp_database_name, "--step", "1", "--start", start_time]
    for i in range(client_number):
        arg_string.append("DS:sum" + str(i) + ":GAUGE:2000:U:U")
    arg_string += ["RRA:AVERAGE:0.5:1:600",
                   "RRA:AVERAGE:0.5:6:700",
                   "RRA:AVERAGE:0.5:24:775",
                   "RRA:AVERAGE:0.5:288:797",
                   "RRA:MAX:0.5:1:600",
                   "RRA:MAX:0.5:6:700",
                   "RRA:MAX:0.5:24:775",
                   "RRA:MAX:0.5:444:797",
                   "RRA:MIN:0.5:1:600",
                   "RRA:MIN:0.5:6:700",
                   "RRA:MIN:0.5:24:775",
                   "RRA:MIN:0.5:444:797",
                   ]
    rrdtool.create(arg_string)
    return tmp_database_name


def fill_rrd(tmp_database_name, global_start_time, arr_logs):
    """
    Fills rrd file with information from logs
    :param tmp_database_name: String. Path to the rrd file that will be filled
    :param global_start_time: int. Timestamp of the first record in logs in
epoch
    :param arr_logs: LogParser[]: List of LogParser objects that should be
processed
    :return: {}. 'end_time' time - of the last record in logs,
'absolute_sum' - sum of all latency values in all documents,
'max_value' - max latency value in all documents,
'min_value' - min latency valuein all documents
    """
    min_time = global_start_time
    open_file_exists = True
    absolute_sum = 0
    max_value = 0
    min_value = 0
    while open_file_exists:
        open_file_exists = False
        start_time = min_time
        counter = 0
        cur_sum = 0
        min_time = 0
        update_string = str(start_time)
        end_time_arg = str(start_time)
        for log in arr_logs:
            while log.last_line and start_time == log.time_stamp:
                if not log.success:
                    # log.faults += 1
                    log.read_next()
                    continue
                counter += 1
                if log.latency > max_value:
                    max_value = log.latency
                if log.latency < min_value or min_value == 0:
                    min_value = log.latency
                cur_sum += log.latency
                log.read_next()
            open_file_exists = open_file_exists or log.last_line

            if log.last_line:
                if min_time == 0 or min_time > log.time_stamp:
                    min_time = log.time_stamp
            if counter == 0:
                update_string += ":" + '0'
            else:
                update_string += ":" + str(cur_sum / float(counter))
            absolute_sum += cur_sum
            cur_sum = 0
            counter = 0

        rrd_update(tmp_database_name, update_string)
    return {'end_time': end_time_arg, 'absolute_sum': absolute_sum,
            'max_value': max_value, 'min_value': min_value}


def create_all_images(tmp_database_name, result_directory, client_number,
                      start_time, end_time):
    """
    Creates all-average.png and all-clients.png which depicts average latency
and latency of all clients respectively
    :param tmp_database_name: String. Path to the directory where rrd file is
placed
    :param result_directory: String. Path to the directory where png files will
be placed
    :param client_number: int. Number of clients.
    :param start_time: String. Timestamp of the first record in logs in epoch
    :param end_time: String. Timestamp of the last record in logs in epoch
    """
    colors = {0: "#000000",
              1: "#0000CD",
              2: "#2E8B57",
              3: "#00FF00",
              4: "#8B008B",
              5: "#FFDAB9",
              6: "#FFFF00",
              7: "#FF0000",
              8: "#800000",
              9: "#191970",
              10: "#FF69B4",
              11: "#20B2AA",
              12: "#A9A9A9",
              13: "#00FFFF",
              14: "#9ACD32",
              15: "#C71585",
              16: "#FF8C00",
              17: "#DC143C",
              }

    arg_string_common = [result_directory + "/all-clients.png",
                         "--width", "600",
                         "--height", "200",
                         "--vertical-label", "ms.",
                         "--start", start_time,
                         "--end", end_time,
                         "--step", "1",
                         "-x", "SECOND:1:SECOND:5:SECOND:10:0:%X",
                         ]
    arg_cdef = ["CDEF:sum="]
    arg_all_graphs_tail = []
    tmp = ""

    for i in range(client_number):
        arg_string_common.append(
            "DEF:m" + str(i) + "_num=" + tmp_database_name + ":sum" + str(i) +
            ":AVERAGE")
        arg_cdef[0] += "m" + str(i) + "_num,"
        tmp += ",+"
        arg_all_graphs_tail.append(
            "LINE1:m" + str(i) + "_num" + colors[i] + ":client" + str(i))
    arg_cdef[0] = arg_cdef[0][:-1]
    tmp = tmp[:-2]
    arg_cdef[0] += tmp
    arg_string_common += arg_cdef + ["CDEF:avg=sum," + str(client_number) +
                                     ",/"]
    # Graph with all Clients
    arg_string = (arg_string_common + arg_all_graphs_tail +
                  ["LINE3:avg#FF0000:avg"])
    rrdtool.graph(arg_string)

    # Graph with average value
    arg_string_common[0] = result_directory + "/all-average.png"
    arg_string = arg_string_common + ["LINE1:avg#FF0000:avg"]
    rrdtool.graph(arg_string)


def draw_client_graph(dir_doc, task_dir, number_of_clients):
    """
    Creates two graph files in .png format that depict all client latency and
    average latency and files with fault query results for each client.
    :param dir_doc: string. Path to log files
    :param task_dir: string. Path to the directory where result images will be
stored
    :param number_of_clients: int. The number of clients of test. Defines which
files should be read.
    """

    arr_logs = []
    min_time = 0

    for i in range(number_of_clients):
        tmp_file_name = dir_doc + "/client-" + str(i) + ".log"
        if not os.path.isfile(tmp_file_name):
            print "incorrect number_of_clients parameter or directory"
            exit(1)
        tmp_log_parser = LogParser(tmp_file_name)
        arr_logs.append(tmp_log_parser)

        if tmp_log_parser.time_stamp:
            if min_time == 0:
                min_time = tmp_log_parser.time_stamp
            else:
                min_time = min(min_time, tmp_log_parser.time_stamp)

    if not min_time:
        min_time = 1
    # Create rrd file and fill it
    # Set start_time and end_time_arg less by 1 than actual
    # time for convenience.
    tmp_database_name = create_rrd(
        dir_doc, str(int(min_time) - 1), len(arr_logs))
    start_time_arg = str(int(min_time) - 1)

    # Fill rrd file
    tmp_result = fill_rrd(tmp_database_name, min_time, arr_logs)
    absolute_sum = tmp_result['absolute_sum']
    max_value = tmp_result['max_value']
    min_value = tmp_result['min_value']
    end_time_arg = tmp_result['end_time']

    # Draw graphs
    create_all_images(
        tmp_database_name, task_dir, len(arr_logs),
        start_time_arg, end_time_arg)

    # Write fault/success results to file
    number_of_all_queries = 0
    number_of_all_faults = 0
    fault_results = open(task_dir + "/faults", "w")
    for log in arr_logs:
        fault_results.write(
            str(arr_logs.index(log)) + ": " + str(log.faults) + " " +
            str(log.query_number) + "\n")
        number_of_all_faults += log.faults
        number_of_all_queries += log.query_number
    fault_results.write(
        "ALL: " + str(number_of_all_faults) + " " + str(number_of_all_queries))
    fault_results.close()

    # Write average, max and min values respectively
    value_results = open(task_dir + "/values", "w")
    value_results.write(
        "AVERAGE: " + str(absolute_sum / number_of_all_queries) + " " + "ms")
    value_results.write("\nMIN: " + str(min_value) + " " + "ms")
    value_results.write("\nMAX: " + str(max_value) + " " + "ms")
    value_results.close()
