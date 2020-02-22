import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("../out.csv", index_col="id", parse_dates=True)

print(df.columns)

# Hence the need for better integration.
# I reckon that I can crack it out this evening.
# Put it all
# It'll be on the trains that are over two days. I must have got the calculation the wrong way around.
# Sad times.
# Well, the whole thing needs tightening up anyway. That should be my first order of business.

# And if this is to be my final iteration, I'm going to do it right.

# Interesting.

plt.scatter(df["duration"], df["destination_delay"])

# With a million points...

# So num_stops is x. destination_delay is y. So straight off we can see that i've calculated it wrong.
# Those values should be absolute.
# What would I expect to see? Ideally a straight-line graph.

plt.show()

# Okay.

# THat's the problem with geographical data: we need to attribute it more to an area.
# And that data is encapsulated in weather records.csv. Problem is, it'll be fuckin' massive.
# Likely too big for my PC to run.
