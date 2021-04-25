import configargparse
from glob import glob
import subprocess
import time
import os

if __name__ == '__main__':

    p = configargparse.ArgParser()
    p.add('-s', '--script', required=False, 
                help='base directory for storing micron experiments``')
    p.add('-d', '--directory', required=True, help='name of the experiment, e.g. fafb')
    p.add('-c', '--command', help='submission command (default=sbatch)', default='sbatch')
    p.add('--dryrun', action='store_true', help='print command instead of executing it')

    args = p.parse_args()

    print(f"{args.directory}/*/{args.script}")
    for i, fn in enumerate(glob(f"{args.directory}/*/{args.script}")):

        if not args.dryrun:
            process = subprocess.Popen(f"{args.command} {fn}",
                                        stdout=subprocess.PIPE, 
                                        stderr=subprocess.PIPE,
                                        shell=True)
            print(args.command, fn)
            print(process.stdout.read())
            time.sleep(2)
        else:
            print(args.command, fn)

