import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

from torch.utils.data import DataLoader
from lib import TrainDataset

import matplotlib.pyplot as plt

import numpy as np


torch.manual_seed(1)

epochs = 10

dataset = TrainDataset()
loader = DataLoader(dataset, batch_size=128, shuffle=True, drop_last=True)

input_size = 37
hidden_sizes = [128, 64]
output_size = 1

model = nn.Sequential(nn.Linear(input_size, hidden_sizes[0]),
                      nn.ReLU(),
                      nn.Linear(hidden_sizes[0], hidden_sizes[1]),
                      nn.ReLU(),
                      nn.Linear(hidden_sizes[1], output_size),
                      nn.Softmax(dim=1)).to("cuda")


criterion = nn.MSELoss()
optimiser = optim.Adam(model.parameters())

losses = np.zeros(epochs)

for epoch in range(epochs):

    loss_arr = np.zeros(0)

    for x, y in loader:

        x = x.type(torch.FloatTensor)
        x = x.to("cuda")

        y = y.type(torch.FloatTensor)
        y = y.to("cuda")

        optimiser.zero_grad()

        output = model(x)

        loss = criterion(output.squeeze(), y)

        loss.backward()
        optimiser.step()

        # print("{:.2f}".format(loss.item()))

        loss_arr = np.append(loss_arr, loss.item())

    losses[epoch] = loss_arr.mean()

    plt.plot(loss_arr[:epoch + 1])

    print(losses)

    plt.ylabel("Loss")
    plt.xlabel("Epochs")

    plt.legend(loc="upper right")

    plt.show()
