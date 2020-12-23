import configargparse
from glob import glob
import subprocess

if __name__ == '__main__':

    p = configargparse.ArgParser()
    p.add('-s', '--script', required=False, 
                help='base directory for storing micron experiments``')
    p.add('-d', '--directory', required=True, help='name of the experiment, e.g. fafb')

    args = p.parse_args()



    for fn in glob(f"{args.directory}/*/{args.script}"):

        print("starting", fn)
        process = subprocess.Popen(['sbatch', fn],
                                             stdout=subprocess.PIPE, 
                                             stderr=subprocess.PIPE)
        print(process.stdout.read())

