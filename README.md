#### Required 
* `Python >= 2.7.x`
* `Numpy >= 1.8.1`

#### How to use

* An input file is needed which is a flat text file with the column and row resitions
	* The data must be zero padded and white space delimited.
	* a single `-` will seperate the column constrains and the row constrains.
	* Column constrains are first, then the row constrains.
	* View the `sample_nonogram_x.txt` files so see.
* Use the `run_nonogram_solver.py` file to run the solver:
	* The `-i` flag is required to give the solver the input file name.
	* The `-o` flag is optional so that the solver so that the answer will be written to a file with that name.
		* The defualt value is `output.txt`
	* Ex:
		* `./run_nonogram_solver -i input_file_name.txt`
		* `./run_nonogram_solver -i input_file_name.txt -o output_file_name.txt`

#### Note
* Since backtracking is used, the algorithm get much slower, the larger the board is.
	* This algorithm has known to be very slow for boards that are of size 20 x 20 and larger.

#### Running the example files
* `./run_nonogram_solver.py -i sample_nonogram_1.txt -o sample_output_1.txt`
* `./run_nonogram_solver.py -i sample_nonogram_2.txt -o sample_output_2.txt`
* `./run_nonogram_solver.py -i sample_nonogram_3.txt -o sample_output_3.txt`
	* The third file takes a very long time to complete.