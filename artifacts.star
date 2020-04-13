print('load("@rules_jvm_external//:specs.bzl", "maven")')
print('load("@rules_jvm_external//:defs.bzl", "maven_artifact")')

print('LOCAL_REPO_ARTIFACTS = [')

load("third_party.star", "third_party_dependencies")
third_party_dependencies()

print(']')