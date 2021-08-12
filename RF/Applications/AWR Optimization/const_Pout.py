# Import Modules
from MWO import *
from matplotlib import pyplot as plt
import numpy as np
import MWO
import sys
import time
import timeit
from datetime import datetime

############################# CONFIGURATION OPTIONS ############################

schema_name = "SweepSchema_3053_4x100"
plot_data_graph_name = "Script Values Plot";
freqs = np.linspace(8e9, 12e9, 5, endpoint=True);
scan_name_prefix = "3053_4x100"

max_opt_iter = 300

Plevel_W = .2
Pmax = 20
Pmin = 14
gamma_max = 1
gamma_min = .001
arg_max = 360
arg_min = .001

################################ DEFINE FUNCTIONS ##############################


def runOptimizer(awrde):

	if awrde.Project.Optimizer.Running:
		print("Cannot start optimzier because it is already running!\nAborting.")
		sys.exit()

	awrde.Project.Optimizer.Start()

	st = time.time()
	while awrde.Project.Optimizer.Running:

		num_iter = str(awrde.Project.Optimizer.MaxIterations)
		width = len(num_iter)

		print(f"\r*** OPTIMIZER RUNNING *** (Time Elapsed: {format(round(time.time()-st, 2), '.2f').zfill(6)} s, Iteration: {str(awrde.Project.Optimizer.Iteration).zfill(width)}/{num_iter})", end="")
		time.sleep(0.1)

	et = time.time()
	print(f"\r*** OPTIMIZER FINISHED *** (Time Elapsed: {format(round(time.time()-st, 2), '.2f').zfill(6)} s, Iteration: {str(awrde.Project.Optimizer.Iteration).zfill(width)}/{awrde.Project.Optimizer.MaxIterations})")

def updateFreq(awrde, f, idx=1, delta=1):

	print(f"-> Changing frequency to {f/1e9} GHz")

	# Change project frequencies (b/c otherwise optimizer will run every freq)
	awrde.Project.Frequencies.Clear()
	awrde.Project.Frequencies.AddMultiple([f])

	# Change optimizer goal frequency
	awrde.Project.OptGoals(idx).xStart = f - delta
	awrde.Project.OptGoals(idx).xStop = f + delta

def saveOptResults(awrde, data, g):

	# Create output dictionary
	nd = dict()

	# Scan over each optimization variable and save to dictionary
	for idx in range(1, awrde.Project.Optimizer.Variables.Count + 1):
		nd[awrde.Project.Optimizer.Variables.Item(idx).Name] = awrde.Project.Optimizer.Variables.Item(idx).Nominal

	# Scan over each value in graph and save to dictionary
	for idx in range(1, g.Measurements.Count + 1):
		nd[g.Measurements.Item(idx).Name] = g.Measurements.Item(idx).TraceValues(1)

	data.append(nd)

############################# INITIALIZE CONNECTION ############################

# Initialize connection to Microwave Office
import win32com.client
awrde = win32com.client.Dispatch("MWOApp.MWOffice")

if not awrde.Project.Schematics.Exists(schema_name):
	print(f"Cannot find schematic '{schema_name}' needed for sweep.\n\nAborting.")
	sys.exit()
else:
	print(f"-> Found schematic '{schema_name}'.")



############################# CONFIGURE OPTIMIZER ##############################

# Start from a clean slate
awrde.Project.OptGoals.RemoveAll()
print("-> Removed old optimizer goals.")

# Create optimizer goal
w = 1
L = 2
xStart = 7.99e9
xStop = 8.01e9
yStart = Plevel_W
yStop = Plevel_W
xUnit = MWO.mwUT_Frequency
yUnit = MWO.mwUT_Frequency
og = awrde.Project.OptGoals.AddGoal(f"{schema_name}.AP_HB", f"PT(PORT_2)", MWO.mwOGT_Equals, w, L, xStart, xStop, xUnit, yStart, yStop, yUnit)

# Print summary of optimizer goals
print(f"-> Created new optmizer goals.\n")
print("****************************** OPTIMIZATION GOALS ***************************")
printGoals(awrde)




# Specify optimization variables
vars = []
vars.append(dict(Name=":Pin", Enabled=True, Maximum=Pmax, Minimum=Pmin, Constrained=True, Found=False))
vars.append(dict(Name=":MagGamma", Enabled=True, Maximum=gamma_max, Minimum=gamma_min, Constrained=True, Found=False))
vars.append(dict(Name=":ArgGamma", Enabled=True, Maximum=arg_max, Minimum=arg_min, Constrained=True))

# Check that optimization variables are correctly configured
for idx in range(1, awrde.Project.Optimizer.Variables.Count + 1):

	# Check if variable is listed in 'vars'
	vidx = 0;
	found = False
	for v in vars:

		if v["Name"] == awrde.Project.Optimizer.Variables.Item(idx).Name:
			vf = v
			found = True
			break

		vidx += 1

	if not found:
		# Variable was not found, disbale and continue
		awrde.Project.Optimizer.Variables.Item(idx).Enabled = False
		continue


	# Copy parameters from 'vars' into AWRDE
	awrde.Project.Optimizer.Variables.Item(idx).Enabled = vf["Enabled"]
	awrde.Project.Optimizer.Variables.Item(idx).Maximum = vf["Maximum"]
	awrde.Project.Optimizer.Variables.Item(idx).Minimum = vf["Minimum"]
	awrde.Project.Optimizer.Variables.Item(idx).Constrained = vf["Constrained"]

	vf["Found"] = True
	vars[vidx] = vf

print("\n*************************** OPTIMIZATION VARIABLES ***************************")
printOptVars(awrde)

foundAll = True
for v in vars:

	if not v["Found"]:
		foundAll = False
		break

if not foundAll:
	print("\nSome optimization variables are missing!\nAborting.");
	sys.exit()
else:
	print("\n-> Optimization variables successfully configured.");

# Set maximum number of optimizer iterations
awrde.Project.Optimizer.MaxIterations = max_opt_iter

# Find plot graph
g = None
for i in range(1, awrde.Project.Graphs.Count + 1):

	if awrde.Project.Graphs.Item(i).Name == plot_data_graph_name:
		g = awrde.Project.Graphs.Item(i)

# Check that plot graph exists
if g is None:
	print(f"Failed to find graph.\nAborting.")
	sys.exit()

# Loop over all values and run optimizer
data = []
for f in freqs:
	updateFreq(awrde, f)
	runOptimizer(awrde)

	saveOptResults(awrde, data, g)

ts = datetime.now().strftime("%d-%b-%Y %H%M")
np.save(f"scan_{scan_name_prefix}_{ts}.npy", data)
# Reformat data into nice shape
# Pin = []
# MagGamma = []
# ArgGamma = []
# I = []
# V = []
# f = []
#
# for data