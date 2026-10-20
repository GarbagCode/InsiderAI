import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import numpy as np

def train_regression_model(df):
    """Train XGBoost regression model to predict returns after congressional trades"""
    
    # Remove rows with NaN target
    df = df.dropna(subset=['target_return'])
    
    # Encode categorical variables
    le_transaction = LabelEncoder()
    le_party = LabelEncoder()
    le_chamber = LabelEncoder()
    
    df['transaction_encoded'] = le_transaction.fit_transform(df['transaction_type'])
    df['party_encoded'] = le_party.fit_transform(df['party'])
    df['chamber_encoded'] = le_chamber.fit_transform(df['chamber'])
    
    # Features (exclude non-numeric and target)
    X = df[['transaction_encoded', 'trade_size_usd', 'party_encoded', 'chamber_encoded', 'days_to_file']]
    y = df['target_return']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    print(f"Training set: {len(X_train)} samples")
    print(f"Test set: {len(X_test)} samples")
    
    # Train model
    model = xgb.XGBRegressor(
        objective='reg:squarederror',
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
        random_state=42
    )
    
    model.fit(X_train, y_train)
    
    # Evaluate
    train_r2 = model.score(X_train, y_train)
    test_r2 = model.score(X_test, y_test)
    
    print(f"\nModel Performance:")
    print(f"Train R² Score: {train_r2:.4f}")
    print(f"Test R² Score: {test_r2:.4f}")
    
    # Feature importance
    feature_names = ['transaction_type', 'trade_size_usd', 'party', 'chamber', 'days_to_file']
    importances = model.feature_importances_
    
    print(f"\nFeature Importance:")
    for name, importance in sorted(zip(feature_names, importances), key=lambda x: x[1], reverse=True):
        print(f"  {name}: {importance:.4f}")
    
    return model, le_transaction, le_party, le_chamber

if __name__ == "__main__":
    import pandas as pd 

    df = pd.read_csv("data/training_data_sell_in_15_days.csv")    
    model, le_transaction, le_party, le_chamber = train_regression_model(df)

    print(model, le_transaction, le_party, le_chamber)