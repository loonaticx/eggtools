"""
Use this to check for models with non-empty UVMap names (known to cause issues)
"""

import os
import sys
import glob
from panda3d.core import Filename
from eggtools.EggMan import EggMan
from eggtools.attributes.EggUVNameAttribute import EggUVNameAttribute
import argparse

# region argparse setup
parser = argparse.ArgumentParser(
    prog = 'egg-uv-remover',
    epilog = 'Removes UV names off given egg file(s).',
    description = 'python -m eggtools.scripts.UVNameRemover input.egg -o output.egg'
)

parser.add_argument(
    'input_egg',
    help = 'Input egg file or wildcard pattern'
)

parser.add_argument(
    '-o',
    '--output',
    type = str,
    nargs = '?',
    help = 'Output egg filename. Only works if a single input file is provided.'
)

parser.add_argument(
    '--inplace',
    default = False,
    action = 'store_true',
    help = 'If this option is given, the input egg files will be rewritten in place with the results.'
)

args = parser.parse_args()
# endregion

# Handle wildcard input
input_files = sorted(glob.glob(args.input_egg))
if not input_files:
    print("Error: No files matched the input pattern!")
    sys.exit()

if len(input_files) > 1 and args.output:
    print("Error: Output filename can only be specified for a single input file.")
    sys.exit()

# Process each file
for input_loc in input_files:
    input_egg = Filename.fromOsSpecific(input_loc)

    # Determine output location
    if args.inplace:
        output_file = input_egg
    else:
        output_loc = args.output if args.output else os.path.splitext(input_loc)[0] + "-no_uvnames.egg"
        output_file = Filename.fromOsSpecific(os.path.join(os.getcwd(), output_loc))

    eggman = EggMan([input_egg])
    eggdata = eggman.get_egg_by_filename(input_egg)
    ctx = eggman.egg_datas[eggdata]

    # Remove UV names
    for eggattr in ctx.egg_attributes:
        if isinstance(eggattr, EggUVNameAttribute):
            print(f"Removing {eggattr} from {ctx.filename}")
            eggattr.apply(eggdata, ctx)
            ctx.dirty = True

    if ctx.dirty:
        eggman.write_egg(eggdata, output_file)
        print(f"Processed {input_loc} -> {output_file}")
    else:
        print(f"Couldn't find a UVNameAttribute in {ctx.filename}, not doing anything.")
