#!/bin/bash
# Wrapper script to install databricks requirements

# in databricks json:
# {
#     "spark_python_task": {
#         ...
#     },
#     "init_scripts": [{
#         "s3": {
#             "destination": f"s3://{CODE_BUCKET}/{CODE_PREFIX}/{{{{ params.code_version }}}}/scripts/databricks.sh",
#             "region": "us-east-1"
#         }
#     }]
# }

set -e  # Exit immediately if a command fails

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Get the root directory of the project
ROOT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

pip install -r "$ROOT_DIR/requirements.txt" --quiet