import pandas as pd
from pydantic import Field
from typing import List
from ddi_fw.datasets import BaseDataset
from keras.datasets import mnist
import numpy as np
from keras.utils import to_categorical

class MNISTDataset(BaseDataset):
    dataset_name: str = Field(default="default", description="MNIST Dataset")
    columns: List[str] = ["image"]
    class_column: str = "label"

    def prep(self):
        (X_train, y_train), (X_test, y_test) = mnist.load_data()
        # Normalize and expand dims if needed
        X_train = X_train.astype(np.float32) / 255.0
        X_test = X_test.astype(np.float32) / 255.0

        # Add channel dimension (for CNNs expecting 3D input per sample)
        X_train = np.expand_dims(X_train, axis=-1)  # shape: (num_samples, 28, 28, 1)
        X_test = np.expand_dims(X_test, axis=-1)
        
        self.X_train = X_train[0:1000]  # Use a subset for faster testing
        self.y_train = y_train[0:1000]  # Use a subset for faster testing
        self.X_test = X_test[0:100]
        self.y_test = y_test[0:100]
        
        self.y_train = to_categorical(self.y_train, num_classes=10)
        self.y_test = to_categorical(self.y_test, num_classes=10)
        
        # # Save as DataFrame or appropriate format your framework uses
        self.dataframe = pd.DataFrame({
            "image": list(X_train) + list(X_test),
            "label": list(y_train) + list(y_test)
        })
    
    # def load(self):
    #     self.prep()
    #     # Split into train/test sets
    #     train_size = 1000  # Adjust based on how many samples you want for training
        
    #     # Create train/val splits if needed
    #     # from sklearn.model_selection import train_test_split, StratifiedKFold
    #     # self.X_train, self.X_val, self.y_train, self.y_val = train_test_split(
    #     #     self.X_train, self.y_train, test_size=0.2, random_state=42
    #     # )
        
  
        