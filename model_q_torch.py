import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F

import os

class QNetworkTorch(nn.Module):
    def __init__(self, input_size=1, hidden_1_size=3, hidden_2_size=3, output_size=4):
        super(QNetworkTorch, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_1_size)
        self.fc2 = nn.Linear(hidden_1_size, hidden_2_size)
        self.fc3 = nn.Linear(hidden_1_size, output_size)

    def save(self, meta=None, name="model"):
        model_folder_path = 'saves'
        if not meta:
            name = f"{name}.pth"
        else:
            name = f"{name}_{meta}.pth"
        file_name = os.path.join(model_folder_path, name)
        print(file_name)
        torch.save(self.state_dict(), file_name)

    def forward(self, x):
        #x = self.relu(self.fc1(x))
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        #print(x)
        #x = self.sigmoid(self.fc2(x))
        l = self.fc3(x)
        #print(f"{x=}")
       # print(f"{l=}")
       # print(f"weight: {self.fc1.weight}")
       # print(f"bias: {self.fc1.bias}")
        return l


class QTrainer:
    def __init__(self, model, lr, gamma):
        self.lr = lr
        self.gamma = gamma
        self.model = model
        self.optimizer = optim.Adam(model.parameters(), lr=self.lr)
        self.criterion = nn.MSELoss()

    def train_step(self, state, action, reward, next_state, done):
        state = torch.tensor(state, dtype=torch.float)
        next_state = torch.tensor(next_state, dtype=torch.float)
        action = torch.tensor(action, dtype=torch.long)
        reward = torch.tensor(reward, dtype=torch.float)



        if len(state.shape) == 1:
            state = torch.unsqueeze(state, 0)
            next_state = torch.unsqueeze(next_state, 0)
            action = torch.unsqueeze(action, 0)
            reward = torch.unsqueeze(reward, 0)
            done = (done,)


        pred = self.model(state)
        #print(done)
        #print(len(done))

        target = pred.clone()
        #print(pred)
        for idx in range(len(done)):
            Q_new = reward[idx]
            if not done[idx]:
                Q_new = reward[idx] + self.gamma * torch.max(self.model(next_state[idx]))

            target[idx][torch.argmax(action[idx]).item()] = Q_new


        self.optimizer.zero_grad()
        loss = self.criterion(target, pred)
        loss.backward()

        self.optimizer.step()

