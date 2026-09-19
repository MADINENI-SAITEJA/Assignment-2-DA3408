import csv
import os
import random

random.seed(42)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SHARDS_DIR = os.path.join(BASE_DIR, "shards")

os.makedirs(SHARDS_DIR, exist_ok=True)

invalid_counts = [1, 2, 3, 4, 5, 6, 7, 8]

names = [
    "Alice", "Bob", "Charlie", "David",
    "Emma", "Frank", "Grace", "Henry"
]

domains = [
    "gmail.com",
    "yahoo.com",
    "outlook.com"
]

for shard_id in range(8):

    rows = []

    invalid_count = invalid_counts[shard_id]

    for i in range(20):

        user_id = shard_id * 20 + i + 1
        name = names[i % len(names)]
        email = f"user{user_id}@{domains[i % len(domains)]}"
        age = 20 + (i % 30)

        rows.append({
            "user_id": user_id,
            "name": name,
            "email": email,
            "age": age
        })

    for i in range(invalid_count):

        row = rows[i]

        if i % 2 == 0:
            row["email"] = "invalid-email"
        else:
            row["name"] = ""

    path = os.path.join(
        SHARDS_DIR,
        f"shard_{shard_id}.csv"
    )

    with open(path, "w", newline="") as f:

        writer = csv.DictWriter(
            f,
            fieldnames=["user_id", "name", "email", "age"]
        )

        writer.writeheader()
        writer.writerows(rows)

    print(
        f"{path}: "
        f"{len(rows)} rows, "
        f"{invalid_count} invalid rows"
    )