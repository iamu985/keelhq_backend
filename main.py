import os
import asyncio
from devtools import pprint
from scripts.test_engine import test_connection
from scripts.test_settings import test_settings

RUNNERS = {
    "test_connection": [test_connection, True],
    "test_settings": [test_settings, False],
}


if __name__ == "__main__":
    running = True
    count = 1
    indexes = [name for name in RUNNERS.keys()]

    while running:
        os.system("clear")
        help = """
        Select the number of the test to run.
        """

        for index, name in enumerate(RUNNERS.keys()):
            help += f"\n[{index + 1}] {name}"

        print(help)

        cmd = input("Enter Number [q/e] to exit: ")
        if cmd == "q" or cmd == "e":
            running = False
            print("Exiting the program.")

        else:
            index = int(cmd) - 1
            func, run_async = RUNNERS[indexes[index]]
            if run_async:
                result = asyncio.run(func())
                pprint(result)
            else:
                result = func()
                pprint(result)
            cont = input("Continue[y/n]: ")
            if cont == "n":
                running = False
                print("Exiting the program.")
