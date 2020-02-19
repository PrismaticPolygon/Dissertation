import torch
import pandas as pd
import numpy as np

from torch.utils.data import DataLoader, Dataset


class TrainDataset(Dataset):

    def __init__(self):

        self.data = pd.read_csv("out.csv")
        self.data = self.data.drop("id", axis=1)

        self.labels = np.asarray(self.data["destination_delay"])

    def __len__(self):

        return len(self.data.index)

    def __getitem__(self, idx):

        if torch.is_tensor(idx):

            idx = idx.tolist()

        label = self.labels[idx]
        sample = torch.from_numpy(self.data.loc[idx].values.astype(np.int64))

        return sample, label


if __name__ == "__main__":

    dataset = TrainDataset()

    print(dataset)

    loader = DataLoader(dataset, batch_size=64, shuffle=True, drop_last=True)

    for x, y in loader:

        print(x.shape)
        print(y.shape)

        break
