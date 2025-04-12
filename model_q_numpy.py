import numpy as np


class QNetworkNumpy:
    def __init__(self, input_size=1, hidden_size=3, output_size=4, lr=0.01):
        self.w1 = np.random.randn(input_size, hidden_size)
        self.w2 = np.random.randn(hidden_size, output_size)
        self.lr = lr

    def forward(self, x):
        self.h1 = np.maximum(0, np.dot(x, self.w1))  # ReLU
        return np.dot(self.h1, self.w2)  # Выходные Q-значения

    def update(self, state, action, reward, next_state, done, gamma=0.9):
        state = np.array([[state]])
        next_state = np.array([[next_state]])

        q_values = self.forward(state)
        next_q_values = self.forward(next_state)

        target = q_values.copy()
        target[0, action] = reward + (0 if done else gamma * np.max(next_q_values))

        error = target - q_values

        # Градиентный спуск (простейший вариант)
        d_w2 = np.dot(self.h1.T, error)
        d_w1 = np.dot(state.T, np.dot(error, self.w2.T) * (self.h1 > 0))  # Производная ReLU

        self.w2 += self.lr * d_w2
        self.w1 += self.lr * d_w1


# Инициализация сети
q_net_np = QNetworkNumpy()

# Пример обновления сети
q_net_np.update(1.0, 2, 1.0, 0.5, False)
