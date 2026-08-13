from pathlib import Path
from collections import Counter
from pyubx2 import UBXReader
import csv
import time

DATA_FOLDER = Path(r"C:\GNSS_Thesis\data_raw\antarctica_pilot")
RESULT_FOLDER = Path(r"C:\GNSS_Thesis\results")

FILES = [
    "20241010.ubx",
    "20250324.ubx",
]

TARGET_MESSAGES = {
    "NAV-PVT",
    "NAV-SAT",
    "MON-RF",
    "MON-SPAN",
    "RXM-MEASX",
    "RXM-RLM",
}

RESULT_FOLDER.mkdir(parents=True, exist_ok=True)


def audit_file(file_path):
    print("\n" + "=" * 70)
    print(f"Reading: {file_path.name}")
    print(f"File size: {file_path.stat().st_size / 1024**2:.1f} MB")
    print("=" * 70)

    counts = Counter()
    examples = {}
    total_size = file_path.stat().st_size
    message_count = 0
    last_report = 0
    start_time = time.time()

    with open(file_path, "rb") as stream:
        ubr = UBXReader(stream, protfilter=2, quitonerror=0)

        for raw_data, parsed_data in ubr:
            if parsed_data is None:
                continue

            identity = getattr(parsed_data, "identity", "UNKNOWN")
            counts[identity] += 1
            message_count += 1

            if identity in TARGET_MESSAGES and identity not in examples:
                examples[identity] = str(parsed_data)

            if message_count - last_report >= 100000:
                position = stream.tell()
                percent = position / total_size * 100
                elapsed = time.time() - start_time
                print(
                    f"{message_count:,} messages | "
                    f"{percent:.1f}% | "
                    f"{elapsed:.1f} sec"
                )
                last_report = message_count

    print(f"\nFinished: {file_path.name}")
    print(f"Total parsed messages: {message_count:,}")
    return counts, examples


for filename in FILES:
    file_path = DATA_FOLDER / filename

    if not file_path.exists():
        print(f"FILE NOT FOUND: {file_path}")
        continue

    counts, examples = audit_file(file_path)
    stem = file_path.stem
    count_file = RESULT_FOLDER / f"{stem}_message_counts.csv"

    with open(count_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["message_type", "count"])
        for message_type, count in counts.most_common():
            writer.writerow([message_type, count])

    example_file = RESULT_FOLDER / f"{stem}_message_examples.txt"

    with open(example_file, "w", encoding="utf-8") as f:
        for target in sorted(TARGET_MESSAGES):
            f.write("\n" + "=" * 80 + "\n")
            f.write(target + "\n")
            f.write("=" * 80 + "\n")
            if target in examples:
                f.write(examples[target])
            else:
                f.write("NOT FOUND OR NOT DECODED")
            f.write("\n")

    print(f"Saved: {count_file}")
    print(f"Saved: {example_file}")

print("\nALL FILES FINISHED.")
