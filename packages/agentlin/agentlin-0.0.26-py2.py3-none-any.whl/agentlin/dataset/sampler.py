from datasets import Dataset


def create_sampler(dataset: Dataset, shuffle: bool = True, seed: int = 42):
    """Create a sampler for the dataset.

    Arguments:
        dataset (Dataset): The dataset.
        shuffle (bool): Whether to shuffle the dataset.
        seed (int): The seed for random number generation.

    Returns:
        sampler (Sampler): The sampler.
    """
    import torch
    from torch.utils.data import RandomSampler, SequentialSampler

    # use sampler for better ckpt resume
    if shuffle:
        train_dataloader_generator = torch.Generator()
        train_dataloader_generator.manual_seed(seed)
        sampler = RandomSampler(data_source=dataset, generator=train_dataloader_generator)
    else:
        sampler = SequentialSampler(data_source=dataset)

    return sampler
