import numpy as np

from gd_util.utils import *
from gd_util.datacontainer import Container


def main():
    out = fPath(__file__, "out")

    # Create a clean container
    with Container(out) as ct:

        # Explicit directory creation (optional)
        ct.mkdir("results")

        # Create file paths using '/'
        input_file = ct / "inputs/data.npy"

        # Write data
        x = np.arange(10)
        np.save(input_file, x)

        y = x**2
        ct.free("output")  # delete a key
        np.save(ct / "results/output.npy", y)
        np.save(ct / "results/tt/output1.npy", y)

        # Files are automatically registered
        # and can be accessed as attributes
        print("Input file :", ct.data)
        print("Result file:", ct.output)
        print("Result file:", ct.get("output"))

    # Container is now closed, infos.json is written

    # Reopen container later
    ct = Container(out)

    # Attribute access still works
    print("Reloaded:")
    print("  data  ->", ct.data)
    print("  output->", ct.output)

    print("--> Tree:")
    print(ct.tree())


if __name__ == "__main__":
    main()
