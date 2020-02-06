# run_sim - READ ME
This script is intended to be used for the Mesoscale Computational Modeling Research Group in order to run the simulation of data automatically. The script requires a "run_files" directory and a "sim_plan" csv file. The "sim_plan" csv outlines the parameters for the simulations that need to be run. Each row will lead to new run of the simulation with new parameters. The run_files directory contains all of the files necessary to run the simulation, and the script will update the "multiple-batch.sh" send file based on the range provided in the simulation plan. After each successfully completed run of the simulation, the created directory will be compressed to a ".tar.gz" file and the deleted. Once all runs have been completed the script will print the time elapsed.
