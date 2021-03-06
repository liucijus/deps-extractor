#!/usr/bin/python3

import glob
import sys

INPUT_DIR = sys.argv[1]
OUTPUT_DIR = sys.argv[2]

pattern = '/third_party/*.bzl'


def read_bzl(file):
    with open(file, 'r') as f:
        return f.readlines()


IMPORT_LINE = 'load("@core_server_build_tools//:import_external.bzl", import_external = "safe_wix_scala_maven_import_external")'


def join_excludes(content):
    exclude_accu = []

    lines = []
    for line in content:
        if 'excludes = ' not in line:
            if len(exclude_accu) > 0:
                lines.append("excludes = [\n" + "".join(exclude_accu) + "],\n")
            exclude_accu = []
            lines.append(line)
        else:
            exclude_accu.append(line.replace('excludes = ', ''))

    return lines


def convert_excludes(line):
    if 'EXCLUDES' in line:
        return line.replace('\n', '').replace('# EXCLUDES ', 'excludes = "') + '",\n'
    else:
        return line


def convert(content, import_prefix):
    return join_excludes(
        [
            convert_excludes(
                line
                    .replace('//:third_party', 'third_party')
                    .replace(IMPORT_LINE, 'load("' + import_prefix + 'import_external.star", "import_external")')
                    .replace('.bzl', '.star')
            )
            for line in content
            if ":macros.bzl" not in line  # fixme
        ]
    )


def write_star(content, file):
    with open(file, 'w') as f:
        f.writelines(content)


for bzl in glob.glob(INPUT_DIR + pattern) + glob.glob(INPUT_DIR + "/third_party.bzl"):
    bzl_content = read_bzl(bzl)

    file_name = bzl[len(INPUT_DIR):]
    star_content = convert(bzl_content, '../..' + bzl[len(INPUT_DIR)])

    output_file = OUTPUT_DIR + '/' + file_name.replace(".bzl", ".star")

    write_star(star_content, output_file)
