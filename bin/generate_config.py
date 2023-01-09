#!/usr/bin/env python
import json
import sys
from pathlib import Path


def get_config_obj(line):
    eq_index = line.index("=")
    key = line[:eq_index].strip()
    value = line[eq_index + 1 :].strip()
    if value.startswith('"') or value.startswith("'"):
        value = value[1:-1]
    return {"name": key, "value": value, "slotSetting": False}


def to_json_file(config, output_file_path):
    with open(output_file_path, "w") as f:
        f.write(json.dumps(config, indent=2))


def skip_line(line):
    if not line:
        return True

    if line.startswith("#"):
        return True

    if line.startswith("COMPOSE_"):
        return True

    return False


if __name__ == "__main__":
    env_file_path = Path(sys.argv[1])
    if (not env_file_path.exists()) or (not env_file_path.is_file()):
        raise Exception("Env file path doesn't exist.")

    output_file_path = env_file_path.parent / "azure-config.json"

    with open(env_file_path) as f:
        config = []
        for line in f:
            line = line.strip()
            if skip_line(line):
                continue
            config.append(get_config_obj(line))
    sorted_config = sorted(config, key=lambda k: k["name"].replace("_", "A"))
    to_json_file(sorted_config, output_file_path)
