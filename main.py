from dotenv import load_dotenv
import modules as generator_modules
import logging as lg
import sys
import json
import gc

load_dotenv()

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"

lg.basicConfig(level=lg.DEBUG,
               format=LOG_FORMAT, stream=sys.stdout)


def main(argv):
    summary = {}
    for module in generator_modules.__all__:
        if module.enabled and len(argv) == 1:
            module.init()
            try:
                lg.info("Processing module [{}]".format(module.__file__))
                result = module.process()
                summary = {**summary, **result}
                gc.collect()
            except Exception as e:
                lg.error(e)
                raise e
        elif hasattr(module, "cmd"):
            if module.cmd == argv[1]:
                module.init()
                module.process()

    if len(argv) == 1:
        with open("data/summary.json", "w") as sumf:
            json.dump(summary, sumf)


if __name__ == "__main__":
    main(sys.argv)
