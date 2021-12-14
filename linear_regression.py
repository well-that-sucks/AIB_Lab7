import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.preprocessing import StandardScaler

class LinearRegression:
    # Set initial params as below(may be revisited some day)
    def __init__(self, learning_rate = 0.05, iterations = 10000):
        self.alpha = learning_rate
        self.iter = iterations
        self.weights, self.bias = None, None # Change it to more safer definition?
        self.loss = []
        
    def mean_squared_error(self, y, y_pred):
        mse = 0
        for i in range(len(y)):
            mse += (y[i] - y_pred[i]) ** 2
        return mse / len(y)
    
    def fit(self, X, y):
        self.weights = np.zeros(X.shape[1])
        self.bias = 0
        for i in range(self.iter):
            y_pred = np.dot(X, self.weights) + self.bias
            loss = self.mean_squared_error(y, y_pred)
            self.loss.append(loss)
            
            partial_w = 2 * (1 / X.shape[0]) * np.dot(X.T, (y_pred - y)) # Make sum function more compact
            partial_b = 2 * (1 / X.shape[0]) * np.sum(y_pred - y)
            
            self.weights -= self.alpha * partial_w
            self.bias -= self.alpha * partial_b
        
        
    def predict(self, X):
        return np.dot(X, self.weights) + self.bias

df = pd.read_csv('results.csv').astype(float)
#max_score = df['Score'].abs().max()
scaler = StandardScaler()
scaler.fit(df)
df_norm = pd.DataFrame(scaler.transform(df), columns = ['Outcome', 'Time', 'Score', 'Algorithm'])
df_norm = df.div(100).round(6)
X = df_norm[['Outcome', 'Time', 'Algorithm']].to_numpy()
Y = df_norm['Score'].to_numpy()

X_train = X[:-5]
X_test = X[-5:]
Y_train = Y[:-5]
Y_test = Y[-5:]

model = LinearRegression()
model.fit(X_train, Y_train)
prediction = model.predict(X_test)
df_predicted = pd.DataFrame({'Outcome': X_test[:, 0], 'Time': X_test[:, 1], 'Algorithm': X_test[:, 2], 'Score_actual': Y_test, 'Score_predicted': prediction}) * 100
df_predicted.to_csv('results_predicted.csv', encoding = 'utf-8', index = False)
print('Weights: ', model.weights)
print('Predicted score: ', prediction * 100)
print('MSE', model.mean_squared_error(Y_test, prediction))