"""
Prepares eggs for cooking.
"""
import sys
import glob
import argparse
from eggtools.utils.EggMaintenanceUtil import EggMaintenanceUtil

# argparse setup
parser = argparse.ArgumentParser(
    prog = 'egg-prepper',
    epilog = 'Prepares eggs for cooking by removing defined UV names, '
             'converting <ObjectTypes> into their literal equivalents, and fixing TRef names.',
    description = 'python -m eggtools.scripts.EggPrepper input.egg [other eggs to process]'
)

parser.add_argument(
    'input_egg',
    help = 'Input egg file or wildcard pattern'
)

parser.add_argument(
    'other_egg_filepaths', nargs = "*", action = "extend", type = str,
    help = 'Additional egg files to process.'
)

args = parser.parse_args()

# Handle wildcard input
all_eggs = sorted(glob.glob(args.input_egg)) + [
    egg for pattern in args.other_egg_filepaths for egg in sorted(glob.glob(pattern))
]

if not all_eggs:
    print("Error: No files matched the input pattern!")
    sys.exit()

# Initialize and perform maintenance
maintainer = EggMaintenanceUtil(file_list = all_eggs)
maintainer.perform_general_maintenance()
print(f"Processed {len(all_eggs)} files.")
