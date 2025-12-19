from torch.utils.data import Dataset


class CachedDataset(Dataset):
    """
    A dataset that caches the results of the delegate dataset.

    Ensures reproducible datasets.
    """

    def __init__(self, delegate: Dataset):
        self.delegate = delegate
        for key in dir(delegate):
            if key.startswith("__"):
                continue
            setattr(self, key, getattr(delegate, key))

        self._cache = [None for _ in range(len(self))]

    def __len__(self):
        return len(self.delegate)  # type: ignore

    def __getitem__(self, index):
        if self._cache[index] is None:
            self._cache[index] = self.delegate[index]
        return self._cache[index]
