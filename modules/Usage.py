import utils.Init as ModuleInit

import utils.DN42Reg as Reg
import json
import time

cmd = "usage"
enabled = True


def init():
    ModuleInit.CheckDir("data/usage")


def process():
    iu4 = Reg.calcIPv4Usage()
    iu6 = Reg.calcIPv6Usage()
    iu = {"created": int(time.time()), "ipv4": iu4, "ipv6": iu6}
    with open("data/usage/usage.json", "w") as f:
        json.dump(iu, f)


if __name__ == "__main__":
    init()
    process()
