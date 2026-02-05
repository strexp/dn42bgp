import argparse
import gc
import logging
import sys
from typing import Any

from modules import asn_detail, build_graph, extract, isp_rank, history

MODULES = {
    "extract": extract, 
    "graph": build_graph, 
    "isp": isp_rank, 
    "asn": asn_detail,
    "history": history
}

EXECUTION_ORDER = [
    "extract",
    "asn",
    "graph",
    "isp",
    "history"
]


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        stream=sys.stdout,
    )


def run_module(name: str, module: Any) -> dict:
    logging.info(f"=== Starting module: {name} ===")
    try:
        result = module.process()
        gc.collect()
        return result if isinstance(result, dict) else {}
    except Exception as e:
        logging.exception(f"Module {name} failed: {e}")
        raise


def main():
    setup_logging()

    parser = argparse.ArgumentParser(description="DN42 Registry Data Generator")
    parser.add_argument(
        "module", nargs="?", help="Specific module to run", choices=MODULES.keys()
    )
    args = parser.parse_args()

    if args.module:
        run_module(args.module, MODULES[args.module])
    else:
        for name in EXECUTION_ORDER:
            run_module(name, MODULES[name])

    logging.info("All tasks completed.")


if __name__ == "__main__":
    main()
