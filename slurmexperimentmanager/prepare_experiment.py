""" This code has been adoped from https://github.com/nilsec/micron """

import os
import sys
from shutil import copyfile, rmtree, copytree
import configargparse
import configparser
import click

def generate_slurm_script(job_name, root_dir, python_binary, run_file, arguments):

    # turn all kwargs into a commandline argutment string
    # in the fromat --key=value



    sbatch_script = f"""#!/bin/bash

#SBATCH --job-name={job_name}
#SBATCH --nodes=1
#SBATCH --partition gpu
#SBATCH --cpus-per-task=8
#SBATCH --gres=gpu:1
#SBATCH --mem=32GB
#SBATCH --chdir={root_dir}

export PYTHONPATH=$PYTHONPATH:{root_dir}

{python_binary} {run_file} {arguments} --default_root_dir {root_dir}
"""

    return sbatch_script

def get_folder_name(path):
    split = os.path.split(path)
    if split[1] == "":
        return os.path.split(split[0])[1]
    else:
        return split[1]
    

def set_up_experiment(base_dir,
                      python_binary,
                      code_dir,
                      run_file,
                      experiment,
                      train_number,
                      clean_up=False,
                      arguments=""):

    ''' Sets up the directory structure and config file for 
        training a network for microtubule prediction.
    Args:
        base_dir (``string``):
            The base directory for storing all experiments and data.
        experiment (``string``):
            The name of the experiment this training run belongs to.
        train_number (``int``):
            The number/id of the training run.
        clean_up (``bool``):
            If true removes the specified train directory
    '''

    base_dir = os.path.expanduser(base_dir)
    setup_dir = os.path.join(base_dir, experiment, "01_train/setup_t{}".format(train_number))

    if clean_up:
        if __name__ == "__main__":
            if click.confirm('Are you sure you want to remove {} and all its contents?'.format(setup_dir), default=False):
                rmtree(setup_dir)
            else:
                print("Abort clean up.")
                return
        else:
            rmtree(setup_dir)
    else:
        if not (os.path.exists(setup_dir)):
            try:
                os.makedirs(setup_dir)
            except:
                raise ValueError("Cannot create setup {}, path invalid".format(setup_dir))
        else:
            raise ValueError("Cannot create setup {}, setup exists already.".format(setup_dir))

        library_name = get_folder_name(code_dir)
        copytree(code_dir, os.path.join(setup_dir, library_name))

        train_script = generate_slurm_script(experiment, setup_dir, python_binary, run_file, arguments)

        with open(os.path.join(setup_dir, "train.sh"), "w") as f:
            f.write(train_script)



def create_run_command():

    config = configparser.ConfigParser()
    config.add_section('Worker')
    if singularity == None or singularity == "None" or not singularity:
        config.set('Worker', 'singularity_container', str(None))
    else:
        config.set('Worker', 'singularity_container', str(singularity))
    config.set('Worker', 'num_cpus', str(5))
    config.set('Worker', 'num_block_workers', str(1))
    config.set('Worker', 'num_cache_workers', str(5))
    if queue == None or queue == "None" or not queue:
        config.set('Worker', 'queue', str(None))
    else:
        config.set('Worker', 'queue', str(queue))
    if mount_dirs == None or mount_dirs == "None" or not mount_dirs:
        config.set('Worker', 'mount_dirs', "None")
    else:
        config.set('Worker', 'mount_dirs', mount_dirs)
    return config



if __name__ == "__main__":

    p = configargparse.ArgParser()
    p.add('-d', '--base_dir', required=False, 
      help='base directory for storing micron experiments``')
    p.add('-e', required=True, help='name of the experiment, e.g. fafb')
    p.add('-t', required=True, help='train number/id for this particular run')
    p.add('-r', required=True, help='script to run')
    p.add('-p', default='python', help='path to python binary')
    p.add('-l', help='path to experiment library')
    p.add('-c', required=False, action='store_true', help='clean up - remove specified train setup')
    p.add('--args', required=False, default="", help='arguments passed to the running script')
    options = p.parse_args()

    experiment_run_file = options.r
    base_dir = options.base_dir
    experiment = options.e
    python_binary = options.p
    code_dir = options.l
    train_number = int(options.t)

    clean_up = bool(options.c)
    set_up_experiment(base_dir,
                      python_binary,
                      code_dir,
                      experiment_run_file,
                      experiment,
                      train_number,
                      clean_up,
                      options.args)