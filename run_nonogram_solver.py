#!/usr/bin/python
import nonogram_solver
import argparse
parser = argparse.ArgumentParser()

parser.add_argument(
	"-i",
	"--input",
	help="input file name",
)
parser.add_argument(
	"-o",
	"--output",
	default="output.txt",
	help="output file name",
)

args = parser.parse_args()

print args.input
nonogram_solver.solve(input_file_name=args.input,output_file_name=args.output)