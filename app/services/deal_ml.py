import pandas as pd
from sklearn.linear_model import LogisticRegression
import pickle

# Example: Simple deal prediction model
# Features: amount, stage, company_size
# Target: won (1) or lost (0)

def train_deal_model():
    # Example training data with more features
    data = {
        'amount': [1000, 5000, 2000, 7000, 3000],
        'stage': [1, 2, 1, 3, 2],
        'company_size': [10, 50, 20, 100, 30],
        'contact_count': [2, 5, 1, 8, 3],
        'email_count': [10, 20, 5, 30, 15],
        'days_open': [5, 10, 3, 20, 7],
        'won': [0, 1, 0, 1, 1]
    }
    df = pd.DataFrame(data)
    X = df[['amount', 'stage', 'company_size', 'contact_count', 'email_count', 'days_open']]
    y = df['won']
    model = LogisticRegression()
    model.fit(X, y)
    # Save model
    with open('deal_model.pkl', 'wb') as f:
        pickle.dump(model, f)
    print('Model trained and saved.')


def predict_deal(amount, stage, company_size):
    with open('deal_model.pkl', 'rb') as f:
        model = pickle.load(f)
    # Add new features: contact_count, email_count, days_open
    X = pd.DataFrame([[amount, stage, company_size, 2, 10, 5]],
        columns=['amount', 'stage', 'company_size', 'contact_count', 'email_count', 'days_open'])
    prediction = model.predict(X)[0]
    return prediction

if __name__ == '__main__':
    train_deal_model()
    # Example prediction
    result = predict_deal(4000, 2, 40)
    print('Prediction (won=1, lost=0):', result)
