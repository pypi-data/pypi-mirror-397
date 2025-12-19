# tree-diet

Implementation of the tree diet algorithm, reducing the treewidth of a graph through min cardinality edge deletion.
Code used for numerical experiments in companion paper: https://hal.inria.fr/hal-03206132/.
Source code documentation available at: https://bmarchand-perso.gitlab.io/tree-diet/.
 
## installation (Linux, MacOS)

Cloning:

    git clone https://gitlab.inria.fr/amibio/tree-diet.git
    cd tree-diet

Installing dependencies (pybind11, numpy, pytest) and setting up the environment:

    python3 -m pip install -r requirements.txt
    . ./setenv.sh 

Then, if you are on linux: 

    make

If you are on mac:

    make macos

Finally, in either case:

    make check

to launch the tests. If they all pass, you are good to go.

## Source code documentation

A Sphinx-based source code documentation, with minimal execution examples, is
available at: https://bmarchand-perso.gitlab.io/tree-diet/.
