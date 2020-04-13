def parse_artifact(artifact):
    parts = artifact.split(':')

    if len(parts) == 3:
        return {
            'group_id': parts[0],
            'artifact_id': parts[1],
            'version': parts[2],
        }
    elif len(parts) == 4:
        fail('Artifact pattern not tested yet' + artifact)
        return {
            'group_id': parts[0],
            'artifact_id': parts[1],
            'classifier': parts[2],
            'version': parts[3],

        }
    else:
        # com.google.inject:guice:jar:no_aop:4.2.0
        return {
            'group_id': parts[0],
            'artifact_id': parts[1],
            'packaging': parts[2],
            'classifier': parts[3],
            'version': parts[4],
        }


def import_external(
        name,
        artifact,
        artifact_sha256=None,
        srcjar=None,
        srcjar_sha256=None,
        deps=[],
        runtime_deps=[],
        snapshot_sources=None,
        excludes=[],
):
    if len(excludes) == 0:
        print('"' + artifact + '",')
    else:
        coords = parse_artifact(artifact)
        lines = ['maven.artifact(']
        params = []
        params.append('group = "' + coords['group_id'] + '"')
        params.append('artifact = "' + coords['artifact_id'] + '"')
        params.append('version = "' + coords['version'] + '"')

        if 'classifier' in coords:
            params.append('classifier = "' + coords['classifier'] + '"')

        lines.append('    ' + ', '.join(params) + ',')

        if len(excludes) > 0:
            lines.append('exclusions = [')
            for exclude in excludes:
                parts = exclude.split(':')
                if len(parts) == 2 and parts[1] != '':
                    lines.append("'" + exclude + "',")
                else:
                    lines.append("# fixme '" + exclude + "',")
            lines.append('],')

        lines.append(')')

        print('\n'.join(lines) + ',')
