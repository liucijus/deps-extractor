#!/usr/bin/python3

import sys

POM_FILE = sys.argv[1]

import collections
import re
import xml.etree.ElementTree as ET

root = ET.parse(POM_FILE).getroot()
m = 'http://maven.apache.org/POM/4.0.0'
m_ns = '{' + m + '}'
nss = {'m': m}


def short(value):
    return value[len(m_ns):] if value.startswith(m_ns) else value


def make_var(pattern):
    line = re.sub(r'[^0-9a-zA-Z_]', '_', pattern)
    upper = line.upper()
    return upper


def parse_value(text, short_version):
    version_capture = r'\${(.*)}'
    version_match = re.match(version_capture, text)

    if version_match:
        return {
            'type': 'var',
            'version': make_var(version_match.group(1)),
            'pattern': text,
            'var': make_var(short_version),
        }
    else:
        return {
            'type': 'const',
            'version': text,
            'var': make_var(short_version),
        }


def find_vars(properties):
    vars = collections.OrderedDict()
    for p in properties:
        short_version = short(p.tag)
        vars['${' + short_version + '}'] = parse_value(p.text, short_version)

    return vars


def split_by_expression(text):
    parts = []

    current_part = []
    for c in text:
        if c == '$':
            if len(current_part) > 0:
                parts.append(current_part)
                current_part = []
            current_part.append(c)
        elif c == '}':
            current_part.append(c)
            parts.append(current_part)
            current_part = []
        else:
            current_part.append(c)

    if len(current_part) > 0:
        parts.append(current_part)

    return map(lambda chars: ''.join(chars), parts)


def to_bazel_expr(text, vars):
    parts = []

    split_by = split_by_expression(text)

    for part in split_by:
        if part in vars:
            parts.append(vars[part]['var'])
        else:
            parts.append("'" + part + "'")

    return ' + '.join(parts)


def find_deps(deps, vars):
    resolved_deps2 = []

    for dep in deps:
        group = dep.find('m:groupId', nss).text
        artifact_id = dep.find('m:artifactId', nss).text
        version = dep.find('m:version', nss).text
        classifier = dep.find('m:classifier', nss)
        scope = dep.find('m:scope', nss)

        dep_struct = {
            'group': "'" + group + "'",
            'artifact': to_bazel_expr(artifact_id, vars),
            'version': to_bazel_expr(version, vars),
        }

        dep_exclusions = []

        exclusions = dep.find('m:exclusions', nss)
        if exclusions:
            for exclusion in exclusions:
                ex_artifact_id = exclusion.find('m:artifactId', nss).text
                ex_group_id = exclusion.find('m:groupId', nss).text
                dep_exclusions.append({
                    'artifact': ex_artifact_id,
                    'group': ex_group_id,
                })

        dep_struct['exclusions'] = dep_exclusions

        if scope is not None:
            scope_value = scope.text
            if scope_value == 'compile':
                dep_struct['neverlink'] = True
            elif scope_value == 'test':
                dep_struct['testonly'] = True

        if classifier is not None:
            dep_struct['classifier'] = "'" + classifier.text + "'"

        resolved_deps2.append(dep_struct)

    return resolved_deps2


all_vars = find_vars(root.find('m:properties', nss))

all_deps_struct = find_deps(root.find('m:dependencyManagement/m:dependencies', nss), all_vars)


def args_to_string(dep):
    args = []
    for key in dep:
        exclusion_args = []
        if key == 'exclusions':
            for exclusion in dep[key]:
                exclusion_value = exclusion
                args_for_exclusion = "artifact='%s', group='%s'" % (
                    exclusion_value['artifact'], exclusion_value['group'])

                exclusion_arg = 'maven.exclusion(' + args_for_exclusion + ')'
                exclusion_args.append(exclusion_arg)
            if exclusion_args:
                args.append('exclusions=[' + ','.join(exclusion_args) + ']')
        else:
            args.append(key + '=' + str(dep[key]))

    return ', '.join(args)


def print_as_maven_struct(deps):
    lines = []
    for dep in deps:
        lines.append('maven.artifact(' + args_to_string(dep) + '),')

    return lines


def print_vars(vars):
    lines = []
    for var in vars:
        var_value = vars[var]

        if var_value['type'] == 'const':
            lines.append(var_value['var'] + '="' + var_value['version'] + '"')
        else:
            lines.append(var_value['var'] + '=' + var_value['version'])
    return lines


output = []
output.append('load("@rules_jvm_external//:defs.bzl", "maven_install")')
output.append('load("@rules_jvm_external//:specs.bzl", "maven")')
output.append('')

for line in print_vars(all_vars):
    output.append(line)

output.append('')

output.append('MANAGED_DEPS=[')
for line in print_as_maven_struct(all_deps_struct):
    output.append(line)
output.append(']')

print('\n'.join(output))
