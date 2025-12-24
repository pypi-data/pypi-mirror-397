from abc import ABC, abstractmethod
from typing import List, Any, Optional, Dict
import numpy as np
from ddi_fw.ml.model_wrapper import ModelWrapper, Result
from ddi_fw.ml.evaluation_helper import evaluate, Metrics
from ddi_fw.utils import utils
from ddi_fw import utils

import tensorflow as tf


def convert_to_categorical(arr, num_classes):
    """
    This function takes an array of labels and converts them to one-hot encoding
    if they are not binary-encoded. If the array is already in a
    compatible format, it returns the original array.

    Parameters:
    - arr: numpy array with label data (could be binary-encoded or label-encoded)
    - num_classes: number of classes to be used in one-hot encoding

    Returns:
    - The one-hot encoded array if the original array was binary or label encoded
    - The original array if it doesn't require any conversion
    """

    try:
        # First, check if the array is binary-encoded
        if not utils.is_binary_encoded(arr):
            # If the arr labels are binary-encoded, convert them to one-hot encoding
            return tf.keras.utils.to_categorical(np.argmax(arr, axis=1), num_classes=num_classes)
        else:
            print("No conversion needed, returning original array.")
            return arr
    except Exception as e:
        # If binary encoding check raises an error, print it and continue to label encoding check
        print(f"Error while checking binary encoding: {e}")

    try:
        # Check if the array is label-encoded
        if utils.is_label_encoded(arr):
            # If the arr labels are label-encoded, convert them to one-hot encoding
            return tf.keras.utils.to_categorical(arr, num_classes=num_classes)
    except Exception as e:
        # If label encoding check raises an error, print it
        print(f"Error while checking label encoding: {e}")
        # If the arr labels don't match any of the known encodings, raise an error
        raise ValueError("Unknown label encoding format.")

    # If no conversion was needed, return the original array

    return arr


class EnsembleStrategy(ABC):
    """Base class for ensemble strategies"""

    @abstractmethod
    def combine_predictions(self, predictions: List[np.ndarray]) -> np.ndarray:
        """Combine individual predictions into ensemble prediction"""
        pass

    @abstractmethod
    def get_strategy_name(self) -> str:
        """Return strategy name"""
        pass


class VotingStrategy(EnsembleStrategy):
    """Majority voting strategy for classification"""

    def combine_predictions(self, predictions: List[np.ndarray]) -> np.ndarray:
        import numpy as np
        from collections import Counter
        predictions_array = np.array(predictions)
        pred_labels = np.array([p.argmax(axis=1) for p in predictions_array])
        return np.apply_along_axis(
            lambda x: Counter(x).most_common(1)[0][0],
            axis=0,
            arr=pred_labels
        )

    def get_strategy_name(self) -> str:
        return "voting"


class AveragingStrategy(EnsembleStrategy):
    """Averaging strategy for regression or probability outputs"""

    def combine_predictions(self, predictions: List[np.ndarray]) -> np.ndarray:
        return np.mean(np.array(predictions), axis=0)

    def get_strategy_name(self) -> str:
        return "averaging"


class StackingStrategy(EnsembleStrategy):
    """Stacking strategy using a meta-learner"""

    def __init__(self, descriptor, meta_learner: ModelWrapper, base_wrappers: List[ModelWrapper] = [],
                 processor: Optional[Any] = None,
                 processor_config: Optional[Dict[str, Any]] = None):
        self.meta_learner = meta_learner
        self.base_wrappers = base_wrappers
        self.descriptor = descriptor
        self.processor = processor
        self.processor_config = processor_config

    def combine_predictions(self, predictions: List[np.ndarray]) -> np.ndarray:
        # Stack predictions as features for meta-learner
        print("shape of predictions list: ")
        print(len(predictions))
        print("shape of first prediction:")
        print(predictions[0].shape)
        print("shape of stacked predictions before processing:")
        test_data = []
        for pred in predictions:
            test_data.append(pred)
        # test_data = np.stack(test_data, axis=1)
        # print(test_data.shape)
        if self.processor and self.processor_config:
            self.meta_learner.train_data = self.processor().process2(
                self.meta_learner.train_data, self.processor_config)
            self.meta_learner.test_data = self.processor().process2(
                test_data, self.processor_config)
        print("shape of train data")
        print(self.meta_learner.train_data.shape)
        print("shape of train label")
        print(self.meta_learner.train_label.shape)
        # x = np.stack(predictions, axis=1)
        # print("shape of predictions for stacking:", x.shape)
        # self.meta_learner.test_data = x
        print("shape of test data")
        print(self.meta_learner.test_data.shape)
        print("shape of test label")
        print(self.meta_learner.train_label.shape)

        self.fit()
        # self.meta_learner.fit(np.column_stack(predictions), None)
        # stacked_features = np.column_stack(predictions)
        return self.meta_learner.predict()

    def get_strategy_name(self) -> str:
        return self.descriptor

    def fit(self):

        # preds = [b.predict() for b in self.base_wrappers]
        # self.meta_learner.test_data = np.stack(preds, axis=1) #test data should transformed to same shape of training data

        # self.meta_learner.test_data = np.hstack(
        #     [b.predict() for b in self.base_wrappers])

        print("Training meta-learner...")
        best_meta_model, best_meta_key, _ = self.meta_learner.fit()
        self.meta_learner.best_model = best_meta_model

        # self.best_model = best_meta_model

        return best_meta_model, best_meta_key

    def predict(self):
        # Step 3: Feed into meta-model
        pred = self.meta_learner.predict()
        return pred

    # def fit_and_evaluate(self, print_detail=False):
    #     best_model, best_key = self.fit()
    #     pred = self.predict()
    #     print("Stacking Strategy Predictions:")
    #     print(pred)
    #     pred_as_cat = convert_to_categorical(pred, self.num_classes)
    #     logs, metrics = evaluate(
    #         self.meta_learner.test_label, pred_as_cat, info=self.descriptor, print_detail=print_detail)
    #     metrics.format_float()
    #     metrics.set_time(self.meta_learner.elapsed_time)
    #     return logs, metrics, pred


class GenericEnsembleWrapper(ModelWrapper):
    """Generic ensemble wrapper supporting multiple strategies"""

    STRATEGY_MAP = {
        "voting": VotingStrategy,
        "averaging": AveragingStrategy,
        "stacking": StackingStrategy
    }

    def __init__(
        self,
        base_wrappers: List[ModelWrapper],
        meta_learners: List[ModelWrapper],
        meta_learner_processors: Dict[str, Any],
        ensemble_strategies: str,          # now comma separated input
        name: str = "ensemble",
        tracking_service: Optional[Any] = None,
        date: Optional[str] = None
    ):
        self.base_wrappers = base_wrappers
        self.name = name
        self.tracking_service = tracking_service
        self.date = date or utils.utc_time_as_string_simple_format()
        self.ensemble_strategies = ensemble_strategies
        self.meta_learners = meta_learners
        self.meta_learner_processors = meta_learner_processors

        # prediction cache so we don't recompute
        self.wrapper_predictions: Dict[str, np.ndarray] = {}

        self.individual_metrics = {}
        self.ensemble_metrics: Dict[str, Metrics] = {}
        self.result = Result()

    # ---------------------------------------------------------
    # FIT
    # ---------------------------------------------------------
    def fit(self):
        train_label, test_label = None, None

        # if any(getattr(wrapper, 'best_model', None) is not None for wrapper in self.base_wrappers):
        #     # At least one wrapper has best_model set
        #     pass

        train_label, test_label = None, None
        train_idx_arr, val_idx_arr = None, None
        val_labels = []
        inputs = []

        for wrapper in self.base_wrappers:
            train_label = wrapper.train_label
            test_label = wrapper.test_label

            train_idx_arr = wrapper.train_idx_arr
            val_idx_arr = wrapper.val_idx_arr

            if not val_labels:
                for i, (train_idx, val_idx) in enumerate(zip(train_idx_arr, val_idx_arr)):
                    fold_val_labels = train_label[val_idx]
                    val_labels.append(fold_val_labels)
            # Convert the list of arrays to a single numpy array
            all_fold_val_labels = np.concatenate(val_labels)

            print(f"Training base model: {wrapper.descriptor}")
            best_model, _, val_preds_dict = wrapper.fit()
            num_classes = wrapper.num_classes
            wrapper.best_model = best_model
            # pred_train = wrapper.predict()
            # if val_preds_dict is not None:
            print("val_preds_dict")
            print(val_preds_dict)
            for key, value in val_preds_dict.items():
                print(f"Key: {key}, Value shape: {value.shape}")
            # stacked_values = np.concatenate(list(val_preds_dict.values()))
            # stacked_values = np.stack(list(val_preds_dict.values()), axis=1)
            stacked_values = np.vstack(list(val_preds_dict.values()))

            inputs.append(stacked_values)
            # inputs.append(list(val_preds_dict.values()))
      
        # inputs = np.concatenate(inputs, axis=1)
        print("shape of inputs for meta-learner:")
        print(inputs[0].shape)
        self.num_classes = num_classes
        self.test_label = test_label
        print("val labels")
        print(len(val_labels))
        # X_meta_train = np.stack(inputs, axis=1)
        # y_meta_train = train_label
        y_meta_train = all_fold_val_labels
        # print("X_meta_train shape:", X_meta_train.shape)
        print(y_meta_train)
        print("y_meta_train shape:", y_meta_train.shape)

        # Step 3: set the meta-learner's training data
        for meta_learner in self.meta_learners:
            
            # meta_learner.train_data = X_meta_train
            meta_learner.train_data = inputs
            meta_learner.train_label = y_meta_train
            meta_learner.train_idx_arr = train_idx_arr
            meta_learner.val_idx_arr = val_idx_arr
            meta_learner.test_label = test_label
            meta_learner.num_classes = num_classes

        # Parse comma-separated strategies
        self.selected_strategies: List[EnsembleStrategy] = []
        for s in self.ensemble_strategies.split(","):
            s = s.strip().lower()
            if s not in self.STRATEGY_MAP:
                raise ValueError(f"Unknown strategy '{s}'")
            if s == "stacking":
                if not self.meta_learners:
                    raise ValueError(
                        "Meta-learner must be provided for stacking strategy")
                for meta_learner in self.meta_learners:
                    processor_dict = self.meta_learner_processors.get(meta_learner.descriptor)
                    processor = processor_dict.get("processor") if processor_dict else None
                    processor_config = processor_dict.get("processor_config") if processor_dict else None
                    print("processor_dict for stacking:")
                    print(processor_dict)
                    if processor is None:
                        raise ValueError(
                            f"Processor must be provided for meta-learner '{meta_learner.descriptor}' in stacking strategy")
                    
                    if processor_config is None:
                        raise ValueError(
                            f"Processor config must be provided for meta-learner '{meta_learner.descriptor}' in stacking strategy")
                    
                    self.selected_strategies.append(StackingStrategy(descriptor=meta_learner.descriptor,
                                                                     meta_learner=meta_learner, 
                                                                     base_wrappers=self.base_wrappers,
                                                                     processor=processor,
                                                                     processor_config=processor_config))
            else:
                self.selected_strategies.append(self.STRATEGY_MAP[s]())

    # ---------------------------------------------------------
    # PREDICT — with prediction caching
    # ---------------------------------------------------------

    def _compute_and_cache_predictions(self):
        """Compute wrapper predictions only once."""
        if self.wrapper_predictions:
            return  # already computed

        for wrapper in self.base_wrappers:
            descriptor = wrapper.descriptor

            y_pred = wrapper.predict()
            print(f"Predictions from wrapper {descriptor}:")
            print(y_pred)
            print("Shape:")
            print(y_pred.shape)

            # Store raw predictions (strategies want raw data)
            self.wrapper_predictions[descriptor] = y_pred

            # Evaluation for individual wrapper
            y_pred_cat = convert_to_categorical(y_pred, self.num_classes)
            _, wrapper_metrics = evaluate(self.test_label, y_pred_cat)
            wrapper_metrics.set_time(wrapper.elapsed_time)
            wrapper_metrics.format_float()

            self.result.add_metric(descriptor, wrapper_metrics)
            self.individual_metrics[descriptor] = wrapper_metrics
        print(self.wrapper_predictions)
    # ---------------------------------------------------------
    # MAIN PREDICTION PIPELINE
    # ---------------------------------------------------------

    def predict(self):
        # Compute predictions only once
        self._compute_and_cache_predictions()

        pred_list = list(self.wrapper_predictions.values())

        ensemble_outputs = {}

        for strategy in self.selected_strategies:
            strategy_name = strategy.get_strategy_name()

            # Combine predictions
            ensemble_pred = strategy.combine_predictions(pred_list)
            ensemble_pred = convert_to_categorical(
                ensemble_pred, self.num_classes)

            # Evaluate ensemble
            _, metrics = evaluate(self.test_label, ensemble_pred)
            if type(strategy) is StackingStrategy:
                metrics.set_time(strategy.meta_learner.elapsed_time)

            metrics.format_float()

            # token = f"ensemble_{strategy_name}"
            token = strategy_name
            self.ensemble_metrics[token] = metrics
            self.result.add_metric(token, metrics)

            ensemble_outputs[token] = ensemble_pred

        return ensemble_outputs   # multiple ensemble predictions

    # ---------------------------------------------------------
    # FIT AND EVALUATE
    # ---------------------------------------------------------
    def fit_and_evaluate(self):
        self.fit()
        ensemble_preds = self.predict()
        return None, self.result, ensemble_preds
