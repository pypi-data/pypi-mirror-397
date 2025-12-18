import can
import yaml
import json


def load_bus(fn: str) -> can.interface.Bus:
    with open(fn, "r", encoding="utf-8") as f:
        if fn.endswith(".json"):
            o = json.load(f)
        else:
            o = yaml.safe_load(f)
        return can.Bus(**o)
