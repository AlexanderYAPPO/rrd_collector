'''
Created on Dec 12, 2014

@author: alexander
'''


def write_head(file_to_write, relative_path, link):
    file_to_write.write(
        '<!DOCTYPE html>\n' +
        '<html>\n' +
        '<head>' +
        '<meta charset="utf-8">' +
        '<meta http-equiv="X-UA-Compatible" content="IE=edge">' +
        '<meta name="viewport" content="width=device-width,' +
        'initial-scale=1">' +
        '<title>Bootstrap 101 Template</title>' +
        '<link href="' + relative_path +
        'css/bootstrap.min.css" rel="stylesheet">' +
        '<link href="' + relative_path +
        'css/dropdown-menu.css" rel="stylesheet">' +
        '<script src="' + relative_path + 'js/jquery.min.js"></script>' +
        '<script src="' + relative_path + 'js/bootstrap.min.js"></script>' +
        '</script>' +
        '<script> ' +
        '$(function(){' +
        '$("#includedContent").load("' + relative_path + link + '");' +
        '});' +
        '</script>' +
        '</head>'
    )
