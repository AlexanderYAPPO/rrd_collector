'''
Created on Nov 17, 2014

@author: alexander
'''

import os
import re
import csv
import helper


def write_tsv_results(result_list, directory):
    tmp_values = []
    for node in result_list:
        for metric in node:
            if metric != "name":
                tmp_values.append(
                    [metric, ] + node[metric])
    csvfile = open(directory + '/results.tsv', 'wb')
    tvc_writer = csv.writer(csvfile, delimiter='\t')
    rows = zip(*tmp_values)
    for row in rows:
        tvc_writer.writerow(row)
    csvfile.close()


def write_line_fo_file(line_to_write, param, new_result_file, result_tuple):
    if not line_to_write:
        print("Reached unexpected end of file")
        result_tuple.append(None)
        return
    parsed_line = re.search(
        "^" + param + ":\s([0-9]+\.?[0-9]*|nan)\s([a-zA-Z%\s\./]+)$",
        line_to_write)
    if parsed_line is None:
        print("A line didn't match the regexp. The line is")
        print('"' + line_to_write + '"')
        result_tuple.append(None)
        return
    new_result_file.write(
        "\n<p>" + param + ": " + parsed_line.group(1) + ' ' +
        parsed_line.group(2) + '</p>')
    # new_tsv_file.write(parsed_line.group(1) + '\t')
    result_tuple.append(parsed_line.group(1))


def write_monitor_graphs(new_result_file, dir_list):
    """
    Writes data about ganglia monitoring in the file in html format.
    :param mew_result_file: File. HTML file which contains all information
about the test.New results will be written here.
    :param dir_list: [string]. List of directories containing information
about a node.
    """
    nodes_test_results = []
    for node_name in dir_list:
        new_result_file.write("\n<h2>" + node_name.split('/')[-1] + "</h2>")

        node_metrics = {"name": node_name.split('/')[-1]}
        for file_name in os.listdir(node_name + "/images"):
            relative_name = node_name + "/images/" + file_name
            relative_name = relative_name[relative_name.find("img/"):]
            # metric_name = file_name.split("/")[-1][:-4]
            # get the metric name from the file name.
            metric_name = os.path.splitext(file_name)[0]
            new_result_file.write("\n<img src = \"" + relative_name + "\">")
            tmp_file = open(
                node_name + "/" + metric_name + "-log", "r")
            tmp_tuple = []
            tmp_line = tmp_file.readline()
            write_line_fo_file(
                tmp_line, "AVERAGE", new_result_file, tmp_tuple)
            tmp_line = tmp_file.readline()
            write_line_fo_file(
                tmp_line, "MIN", new_result_file, tmp_tuple)
            tmp_line = tmp_file.readline()
            write_line_fo_file(
                tmp_line, "MAX", new_result_file, tmp_tuple)
            tmp_file.close()
            node_metrics[
                metric_name + "_" + node_name.split('/')[-1]
            ] = tmp_tuple

        nodes_test_results.append(node_metrics)
    return nodes_test_results


def write_client_graphs(new_result_file, all_images,
                        client_file_faults, client_file_values):
    """
    Writes data about clients in the file in html format.
    :param mew_result_file: File. HTML file which contains all information
about the test.New results will be written here.
    :param dir_list: [string]. List of all images (graphs) related to clients.
    :param client_file_faults: File. File containing information about faulted
queries.
    :param client_file_values: File. File containing aggregate data about
clients.
    """
    for graphs in all_images:
        relative_name = graphs[graphs.find("img/"):]
        new_result_file.write("\n<img src = \"" + relative_name + "\">")

    for line in client_file_faults:
        content = line.split(' ')
        if content[0][:3] == "ALL":
            new_result_file.write(
                "\n<p>All clients: " + content[1] + " faults out of " +
                content[2] + " queries</p>")
            break
        else:
            new_result_file.write(
                "\n<p>Client #" + content[0] + " " + content[1] +
                " faults out of " + content[2][:-1] + " queries</p>")

    clients_results = {"name": "clients_latency"}
    tmp_tuple = []

    tmp_line = client_file_values.readline()
    write_line_fo_file(
        tmp_line, "AVERAGE", new_result_file, tmp_tuple)

    tmp_line = client_file_values.readline()
    write_line_fo_file(
        tmp_line, "MIN", new_result_file, tmp_tuple)

    tmp_line = client_file_values.readline()
    write_line_fo_file(
        tmp_line, "MAX", new_result_file, tmp_tuple)
    clients_results["latency"] = tmp_tuple
    return clients_results


def result_commit(results_dir, report_dir, task_list, task_name, task_id):
    """
    Add all logs results and graphs to MarkDown files.
    :param result_dir: string. Path to all graphs.
    :param report_dir: string. Path to the directory where all results will be
placed.
    :param task_list: list[string]. Name of the task, represented in list.
Basically, path to task in form of list.
    :param task_name: string. The Name of the task. For example,
'infinispan-embedded-x12'
    :param task_id: int. The unique number for particular task. For example,
you can use end time value of the task.
    """
    dir_list = []
    all_directories = []
    for f in os.listdir(results_dir):
        if os.path.isdir(os.path.join(results_dir, f)):
            all_directories.append(os.path.join(results_dir, f))
    for i_directory in all_directories:
        dir_list.append(i_directory)

    new_result_file = open(report_dir + "/" + task_name + ".html", "w")
    # new_result_file = open(report_dir + "/" + "report.html", "w")
    helper.write_head(
        new_result_file, "../../../../../../../../../",
        "reference_for_leafs.html")
    html_file_title = '<h3>'
    for i in task_list:
        html_file_title += i + ' '
    html_file_title += '<h3>\n'
    new_result_file.write(
        '<body>\n' +
        '<div id="includedContent"></div>' +
        html_file_title)

    result_list = write_monitor_graphs(
        new_result_file, dir_list)
    new_result_file.write("\n<p>Client information</p>")
    all_images = []
    for f in os.listdir(results_dir):
        if os.path.isfile(os.path.join(results_dir, f)) and f[-4:] == ".png":
            all_images.append(os.path.join(results_dir, f))

    client_file_faults = open(results_dir + "/faults", "r")
    client_file_values = open(results_dir + "/values", "r")
    result_list.append(write_client_graphs(
        new_result_file, all_images, client_file_faults,
        client_file_values))
    client_file_faults.close()
    client_file_values.close()

    new_result_file.write(
        "\n</body>\n" +
        "</html>")
    new_result_file.close()

    write_tsv_results(result_list, report_dir)
