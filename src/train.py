import yaml
from .data_preprocessing import DataPreprocessor
from .feature_engineering import FeatureEngineer
from .model import ModelSelector
import logging
import pandas as pd
import joblib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def train_model():
    try:
        # Load configuration
        with open('config/config.yaml', 'r') as f:
            config = yaml.safe_load(f)
        
        # Initialize preprocessor and load data
        preprocessor = DataPreprocessor(config)
        raw_data = preprocessor.load_data()
        train_data, test_data = preprocessor.prepare_data(raw_data)
        
        # Feature engineering
        feature_engineer = FeatureEngineer(config)
        train_data = feature_engineer.create_all_features(train_data)
        test_data = feature_engineer.create_all_features(test_data)
        
        # Model selection
        model_selector = ModelSelector(config)
        best_model, metrics = model_selector.select_best_model(train_data, test_data)
        
        # Save best model
        joblib.dump(best_model, config['output']['model_path'])
        logger.info(f"Best model saved to {config['output']['model_path']}")
        
        # Generate and save predictions
        final_predictions = best_model.predict(test_data)
        pd.DataFrame({
            'ds': test_data['ds'],
            'actual': test_data['y'],
            'predicted': final_predictions
        }).to_csv(config['output']['predictions_path'], index=False)
        
        return metrics
        
    except Exception as e:
        logger.error(f"Error in training pipeline: {str(e)}")
        raise

if __name__ == "__main__":
    train_model() 