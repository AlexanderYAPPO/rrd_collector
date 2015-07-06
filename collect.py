'''
Created on Nov 17, 2014

@author: alexander
'''

"""
Script gets the name of the task, start time, end time, the number of clients,
fetches data from client logs and ganglia's databases and saves results in
'<commonDir>/results' and MarkDown files in <commonDir>/docs.
"""

import rrd_collector
import client_grpah_maker
import result_commit
import sys
import os
import glob
import argparse
import helper
import distutils.core
from multiprocessing import Pool

processes_count = 8


class Tree:

    def __init__(self, node_name):
        self.children = {}
        self.node = node_name

    def add_leaf(self, splitted_list):
        if not splitted_list:
            return
        if not splitted_list[0] in self.children:
            self.children[splitted_list[0]] = Tree(splitted_list[0])
        self.children[splitted_list[0]].add_leaf(splitted_list[1:])


def print_tree(node, file_to_write, path_to_page, relative_path, first):
    absolute_path = relative_path + path_to_page
    if not node.children:
        file_to_write.write(
            '<li><a href="' + absolute_path + node.node +
            '">' + node.node + '</a></li>')
    else:
        new_path = ""
        if first:
            file_to_write.write('<div class="dropdown">\n')
            file_to_write.write(
                '<a id="dLabel" role="button" ' +
                'data-toggle="dropdown" class="btn btn-primary" ' +
                'data-target="#" href="/page.html">\n')
            file_to_write.write('Tests <span class="caret"></span>\n')
            file_to_write.write('</a>\n')
            file_to_write.write(
                '<ul class="dropdown-menu multi-level" role="menu" ' +
                'aria-labelledby="dropdownMenu">\n')
            file_to_write.write('<li class="dropdown-submenu">\n')
            new_path = ""
        else:
            file_to_write.write('<li class="dropdown-submenu">\n')
            file_to_write.write('<a href="#">' + node.node + '</a>\n')
            file_to_write.write('<ul class="dropdown-menu">\n')
            new_path = path_to_page + node.node + "/"
        for child in node.children:
            print_tree(
                node.children[child],
                file_to_write, new_path, relative_path, False)
        if first:
            file_to_write.write('</li>\n')
            file_to_write.write('</ul>\n')
            file_to_write.write('</div>\n')
        else:
            file_to_write.write('</ul>\n')
            file_to_write.write('</li>\n')


def build_tree(tree_list):
    result_tree = Tree("root")
    for task in tree_list:
        splitted = task.split('/')
        result_tree.add_leaf(splitted)
    return result_tree


def collect_iteration(opts, task_dir):
    f = open(task_dir + "/vars_for_collect")
    print ('Processing ' + task_dir)
    tmp_line = f.readline().split('\t')
    task_name = tmp_line[0]
    start_time = tmp_line[1]
    end_time = tmp_line[2]
    number_of_clients = tmp_line[3]
    rrd_collector.draw_all_rrd(
        task_dir + "/ganglia/rrds/cluster/",
        opts.reports_dir + task_dir[len(opts.results_dir):] + "/img",
        start_time,
        end_time)
    client_grpah_maker.draw_client_graph(
        task_dir,
        opts.reports_dir + task_dir[len(opts.results_dir):] + "/img",
        int(number_of_clients))
    result_commit.result_commit(
        opts.reports_dir + task_dir[len(opts.results_dir):] + "/img",
        opts.reports_dir + task_dir[len(opts.results_dir):],
        task_dir[len(opts.reports_dir) + 1:].split('/'),
        task_name,
        end_time)


def run_collect(opts):
    distutils.dir_util.copy_tree("css", opts.reports_dir + "/css")
    distutils.dir_util.copy_tree("fonts", opts.reports_dir + "/fonts")
    distutils.dir_util.copy_tree("js", opts.reports_dir + "/js")
    task_dir_list = glob.glob(opts.results_dir + '/*/*/*/*/*/*/*/*/*')
    pool = Pool(processes=processes_count)
    results = [pool.apply(collect_iteration, args=(opts, task_dir)) for task_dir in task_dir_list]
    #for task_dir in task_dir_list:
    #   collect_iteration(opts, task_dir)
    # creating reference page
    
    html_dir_list = glob.glob(opts.reports_dir + '/*/*/*/*/*/*/*/*/*/*.html')
    tmp_tree = []
    for report_file in html_dir_list:
        tmp_tree.append(report_file[(len(opts.reports_dir) + 1):])
    result_tree = build_tree(tmp_tree)
    f = open(opts.reports_dir + '/index.html', 'w')
    helper.write_head(f, "", "reference.html")
    f.write(
        '<body>\n' +
        '<div class="container">' +
        '<div class="row">' +
        '<h2>Reference</h2>' +
        '<hr>' +
        '<div id="includedContent"></div>' +
        '</div>' +
        '</div>' +
        '</body>' +
        '</html>')
    f.close()
    f = open(opts.reports_dir + '/reference.html', 'w')
    print_tree(result_tree, f, "", "", True)
    f.close()
    f = open(opts.reports_dir + '/reference_for_leafs.html', 'w')
    print_tree(result_tree, f, "", "../../../../../../../../../", True)
    f.close()


def get_args():
    parser = argparse.ArgumentParser(description='Test results collector')
    parser.add_argument(
        '--results-dir', '-rs', type=str, required=True,
        help="Root directory of all test results. Default value is " +
        "/root/results")
    parser.add_argument(
        '--reports-dir', '-rp', type=str, required=True,
        help="Root directory of all reports files. Default value is " +
        "/root/reports")
    opts = parser.parse_args()
    print(opts.__dict__)
    return opts

if __name__ == '__main__':
    options = get_args()
    run_collect(options)
