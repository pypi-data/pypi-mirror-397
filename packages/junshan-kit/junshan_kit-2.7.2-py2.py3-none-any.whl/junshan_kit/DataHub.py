"""
----------------------------------------------------------------------
>>> Author       : Junshan Yin  
>>> Last Updated : 2025-10-28
----------------------------------------------------------------------
"""

import torchvision, torch
import torchvision.transforms as transforms
import pandas as pd
from torch.utils.data import random_split, Subset

from junshan_kit import DataSets, DataProcessor, ParametersHub

def Adult_Income_Prediction(Paras):

    df = DataSets.adult_income_prediction() 
    transform = {
        "train_size": 0.7,
        "normalization": True
    }
    label_col='income'

    train_dataset, test_dataset, transform = DataProcessor.Pandas_TO_Torch(df, label_col).to_torch(transform, Paras)

    return train_dataset, test_dataset, transform


def Credit_Card_Fraud_Detection(Paras):
    df = DataSets.credit_card_fraud_detection()
    transform = {
        "train_size": 0.7,
        "normalization": True
    }
    label_col='Class'

    train_dataset, test_dataset, transform = DataProcessor.Pandas_TO_Torch(df, label_col).to_torch(transform, Paras)

    return train_dataset, test_dataset, transform

def Diabetes_Health_Indicators(Paras):
    df = DataSets.diabetes_health_indicators()
    transform = {
        "train_size": 0.7,
        "normalization": True
    }
    label_col='diagnosed_diabetes'

    train_dataset, test_dataset, transform = DataProcessor.Pandas_TO_Torch(df, label_col).to_torch(transform, Paras)

    return train_dataset, test_dataset, transform

def Electric_Vehicle_Population(Paras): 
    df = DataSets.electric_vehicle_population()
    transform = {
        "train_size": 0.7,
        "normalization": True
    }
    label_col='Electric Vehicle Type'
    train_dataset, test_dataset, transform = DataProcessor.Pandas_TO_Torch(df, label_col).to_torch(transform, Paras)

    return train_dataset, test_dataset, transform

def Global_House_Purchase(Paras): 
    df = DataSets.global_house_purchase()
    transform = {
        "train_size": 0.7,
        "normalization": True
    }
    label_col='decision'
    train_dataset, test_dataset, transform = DataProcessor.Pandas_TO_Torch(df, label_col).to_torch(transform, Paras)

    return train_dataset, test_dataset, transform

def Health_Lifestyle(Paras): 
    df = DataSets.health_lifestyle()
    transform = {
        "train_size": 0.7,
        "normalization": True
    }
    label_col='disease_risk'
    train_dataset, test_dataset, transform = DataProcessor.Pandas_TO_Torch(df, label_col).to_torch(transform, Paras)

    return train_dataset, test_dataset, transform

def Homesite_Quote_Conversion(Paras): 
    df = DataSets.Homesite_Quote_Conversion()
    transform = {
        "train_size": 0.7,
        "normalization": True
    }
    label_col='QuoteConversion_Flag'
    train_dataset, test_dataset, transform = DataProcessor.Pandas_TO_Torch(df, label_col).to_torch(transform, Paras)

    return train_dataset, test_dataset, transform

def TN_Weather_2020_2025(Paras): 
    df = DataSets.TamilNadu_weather_2020_2025()
    transform = {
        "train_size": 0.7,
        "normalization": True
    }
    label_col='rain_tomorrow'
    train_dataset, test_dataset, transform = DataProcessor.Pandas_TO_Torch(df, label_col).to_torch(transform, Paras)

    return train_dataset, test_dataset, transform



def MNIST(Paras, model_name):
    """
    Load the MNIST dataset and return both the training and test sets,
    along with the transformation applied (ToTensor).
    """
    transform = torchvision.transforms.ToTensor()

    train_dataset = torchvision.datasets.MNIST(
        root='./exp_data/MNIST',
        train=True,
        download=True,
        transform=transform
    )

    test_dataset = torchvision.datasets.MNIST(
        root='./exp_data/MNIST',
        train=False,
        download=True,
        transform=transform
    )

    if Paras["model_type"][model_name] == "binary":

        train_mask = (train_dataset.targets == 0) | (train_dataset.targets == 1)
        test_mask = (test_dataset.targets == 0) | (test_dataset.targets == 1)

        train_indices = torch.nonzero(train_mask, as_tuple=True)[0]
        test_indices = torch.nonzero(test_mask, as_tuple=True)[0]

        train_dataset = torch.utils.data.Subset(train_dataset, train_indices.tolist())
        test_dataset = torch.utils.data.Subset(test_dataset, test_indices.tolist())

    return train_dataset, test_dataset, transform


def CIFAR100(Paras, model_name):
    """
    Load the CIFAR-100 dataset with standard normalization and return both
    the training and test sets, along with the transformation applied.
    """
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.5071, 0.4867, 0.4408],   
                            std=[0.2675, 0.2565, 0.2761])     
    ])

    train_dataset = torchvision.datasets.CIFAR100(
        root='./exp_data/CIFAR100',
        train=True,
        download=True,
        transform=transform
    )

    test_dataset = torchvision.datasets.CIFAR100(
        root='./exp_data/CIFAR100',
        train=False,
        download=True,
        transform=transform
    )

    if Paras["model_type"][model_name] == "binary":
        train_mask = (torch.tensor(train_dataset.targets) == 0) | (torch.tensor(train_dataset.targets) == 1)
        test_mask = (torch.tensor(test_dataset.targets) == 0) | (torch.tensor(test_dataset.targets) == 1)

        train_indices = torch.nonzero(train_mask, as_tuple=True)[0]
        test_indices = torch.nonzero(test_mask, as_tuple=True)[0]

        train_dataset = torch.utils.data.Subset(train_dataset, train_indices.tolist())
        test_dataset = torch.utils.data.Subset(test_dataset, test_indices.tolist())

    return train_dataset, test_dataset, transform


def Caltech101_Resize_32(Paras, train_ratio=0.7, split=True):

    transform = transforms.Compose([
        # transforms.Lambda(convert_to_rgb),  
        transforms.Grayscale(num_output_channels=3),
        transforms.Resize((32, 32)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],  
                            std=[0.229, 0.224, 0.225])
    ])
    
    full_dataset = torchvision.datasets.Caltech101(
        root='./exp_data/Caltech101',
        download=True,
        transform=transform
    )

    if split:
        total_size = len(full_dataset)
        train_size = int(train_ratio * total_size)
        test_size = total_size - train_size

        train_dataset, test_dataset = random_split(full_dataset, [train_size, test_size])

    else:
        train_dataset = full_dataset
        # Empty test dataset, keep the structure consistent
        test_dataset = Subset(full_dataset, [])  

    return train_dataset, test_dataset, transform

# <caltech101_Resize_32>