# slurm-experiment-manager

Slurm-experiment-manager is a lightweight python library to manage ML experiments. It's two main functions are to 
1) generate a reproducable snapshot for every individual run
2) automate the slurm submission

An alternative, if you want to manage your experiments with `sacred` is SEML https://github.com/TUM-DAML/seml. In contrast to SEML, this library aims to be very light weight and will not require a mongodb setup.
