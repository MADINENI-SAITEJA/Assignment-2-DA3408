import csv
import json
import os
import re
import socket
import time


EMAIL_RE = re.compile(
    r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
)


def valid_row(row):

    required = ["user_id", "name", "email", "age"]

    for field in required:

        if field not in row:
            return False

        if row[field] is None or str(row[field]).strip() == "":
            return False

    if not EMAIL_RE.match(row["email"]):
        return False

    try:
        age = int(row["age"])
    except ValueError:
        return False

    if age < 18 or age > 100:
        return False

    return True


def main():

    completion_index = int(
        os.environ.get("JOB_COMPLETION_INDEX", "0")
    )

    base_dir = os.path.dirname(
        os.path.abspath(__file__)
    )

    shard_path = os.path.join(
        base_dir,
        "shards",
        f"shard_{completion_index}.csv"
    )

    pod_name = os.environ.get(
        "POD_NAME",
        socket.gethostname()
    )

    node_name = os.environ.get(
        "NODE_NAME",
        "unknown"
    )

    print(
        f"[worker {completion_index}] "
        f"pod={pod_name} "
        f"node={node_name} "
        f"shard={shard_path}",
        flush=True
    )

    invalid_rows = 0
    total_rows = 0

    with open(shard_path, newline="") as f:

        reader = csv.DictReader(f)

        for row in reader:

            total_rows += 1

            if not valid_row(row):
                invalid_rows += 1

    result = {
        "shard": completion_index,
        "total_rows": total_rows,
        "invalid_rows": invalid_rows,
        "pod_name": pod_name,
        "node_name": node_name
    }

    print(
        "RESULT_JSON:" + json.dumps(result),
        flush=True
    )

    hold_seconds = int(
        os.environ.get("HOLD_SECONDS", "0")
    )

    time.sleep(hold_seconds)


if __name__ == "__main__":
    main()