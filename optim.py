import pandas as pd
import numpy as np

from sklearn.model_selection import GridSearchCV

# I don't quite understand how all of these fit together.

params = {
    "bootstrap": [False, True]
}

# grid_search = GridSearchCV()

# Ah. I through in my own CV. I'm currently using.... just cross_val_score. Okay.
# Hm. There's lots of ways I could do this.