# read from json
# programatic pipeline

import unittest
import json
from pathlib import Path
from ddi_fw.datasets.dataset_splitter import DatasetSplitter
from ddi_fw.pipeline import Pipeline, MultiPipeline
from ddi_fw.datasets import BaseDataset
from ddi_fw.langchain.embeddings import MeanPoolingStrategy, PoolingStrategy
from config.mnist_dataset import MNISTDataset

class TestPipeline2(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Read the JSON configuration file
       
        
        config_path = Path('./tests/config/pipeline_test_mnist.json')
        with open(config_path, 'r') as f:
            cls.config = json.load(f)
            print(cls.config)

    def test_pipeline_creation_mnist(self):
        
        config_path = Path('./tests/config/pipeline_test_mnist.json')
        with open(config_path, 'r') as f:
            config = json.load(f)
            print(config)
        
        dataset_splitter = DatasetSplitter()
        pooling_strategy = MeanPoolingStrategy()
        # dataset = MNISTDataset(dataset_name="MNISTDataset",
        #                       dataset_splitter_type = DatasetSplitter ,
        #                       index_path="tests/datasets/mnist/indexes"
        #                    )
        # dataset.load()
        # dataset.split_dataset(save_indexes=True)
        
        # cfg = self.config['experiments'][0]
        # # Create a Pipeline object using the configuration
        # mp = MultiPipeline(experiments_config=self.config).build()
        # mp.run()
        # print(f'name\t accuracy\tf-score\tprecision\trecall')
        # for key in mp.results().keys():
        #     for m in mp.results()[key].metric_dict:
        #         accuracy = mp.results()[key].metric_dict[m].accuracy
        #         macro_f_score = mp.results()[key].metric_dict[m].f1_score['macro']
        #         macro_precision = mp.results()[key].metric_dict[m].precision['macro']
        #         macro_recall = mp.results()[key].metric_dict[m].recall['macro']
        #         print(f'{m}: {accuracy}\t{macro_f_score}\t{macro_precision}\t{macro_recall}')
            
 

if __name__ == '__main__':
    unittest.main()