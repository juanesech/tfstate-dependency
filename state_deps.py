import argparse
import hcl2
from pathlib import Path
import json
import operator

parser = argparse.ArgumentParser(
                    prog='state-deps',
                    description='Describe terraform project interdependency',
                    epilog='Describe terraform state dependencies')

parser.add_argument('domain')
parser.add_argument('-p', '--basepath', default="./tf_templates")
parser.add_argument('-o', '--output', default="baseline.json")
args = parser.parse_args()

proj_dir = args.basepath
domain = args.domain
services = []

for file in Path(proj_dir).rglob('*.tf'):
    service = {}
    service["name"] = str(file).split("/")[-2]
    service["dependsOn"] = []

    with open(file, "r") as f:
        data = f.read()
    parsed = hcl2.loads(data)

    for data_source in parsed["data"]:
        for remote in data_source['terraform_remote_state']:
            ds_path = str(data_source['terraform_remote_state'][remote]["config"]["prefix"]).split("/")
            if ds_path[0] == domain or ds_path[0] == "${local.domain}":
                dep_name = ds_path[-1]
                service["dependsOn"].append(dep_name)
    services.append(service)

services.sort(key=operator.itemgetter('dependsOn'))

f = open(args.output, "w")
f.write(json.dumps(services, indent=2))
f.close()