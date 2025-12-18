#methods: plot_mqq, plot_manhattan

import gwaslab as gl
# Load sumstats

sumstats = gl.Sumstats("mysumstats.txt.gz", fmt="auto")

# run basic_check if necessary

# plot 
sumstats.plot_mqq(mode="m", skip = 2)