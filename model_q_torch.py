import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from noisynetworks import FactorisedNoisyLayer

import os


from icecream import ic

from  config_game import device
class QNetworkTorch(nn.Module):
    def __init__(self, input_size, hidden_1_size, hidden_2_size, output_size, enable_dueling_dqn, flag_noise_bias):
        super(QNetworkTorch, self).__init__()

        self.enable_dueling_dqn = enable_dueling_dqn
        self.flag_noise_bias = flag_noise_bias

        if self.flag_noise_bias:
            self.fc1 = FactorisedNoisyLayer(input_size, hidden_1_size)
            self.fc2 = FactorisedNoisyLayer(hidden_1_size, hidden_2_size)
            self.output = FactorisedNoisyLayer(hidden_1_size, output_size)
        else:
            self.fc1 = nn.Linear(input_size, hidden_1_size)
            self.fc2 = nn.Linear(hidden_1_size, hidden_2_size)
            self.output = nn.Linear(hidden_1_size, output_size)



        if self.enable_dueling_dqn:
            if self.flag_noise_bias:
                # Value stream
                self.fc_value = FactorisedNoisyLayer(hidden_1_size, hidden_1_size)
                self.value = FactorisedNoisyLayer(hidden_1_size, 1)

                # Advantages stream
                self.fc_advantages = FactorisedNoisyLayer(hidden_1_size, hidden_1_size)
                self.advantages = FactorisedNoisyLayer(hidden_1_size, output_size)
            else:
                # Value stream
                self.fc_value = nn.Linear(hidden_1_size, hidden_1_size)
                self.value = nn.Linear(hidden_1_size, 1)

                # Advantages stream
                self.fc_advantages = nn.Linear(hidden_1_size, hidden_1_size)
                self.advantages = nn.Linear(hidden_1_size, output_size)

    def save(self, count_runs, experiment=None, meta=None, name="model"):
        model_folder_path = 'saves'
        model_saves_path = "saves"
        if not meta:
            name = f"{name}.pth"
        else:
            name = f"{name}_{meta}.pth"

        folder = os.path.join(model_folder_path, experiment, model_saves_path, f"run_{count_runs}")
        path = os.path.join(folder, name)

        #os.makedirs(folder, exist_ok=True)

        ic(path)
        torch.save(self.state_dict(), path)



    def forward(self, x):
        #x = self.relu(self.fc1(x))
        if x.dim() == 1:
            x = x.unsqueeze(0)
        #print(x)
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))


        if self.enable_dueling_dqn:
            # Value calc
            v = F.relu(self.fc_value(x))
            V = self.value(v)

            # Advantages calc
            a = F.relu(self.fc_advantages(x))
            A = self.advantages(a)

            # Calc Q
            #print(A)
            Q = V + A - torch.mean(A, dim=1, keepdim=True)

        else:
            Q = self.output(x)

        return Q

        #print(x)
        #x = self.sigmoid(self.fc2(x))
        #l = self.fc3(x)
        #print(f"{x=}")
       # print(f"{l=}")
       # print(f"weight: {self.fc1.weight}")
       # print(f"bias: {self.fc1.bias}")
        #return l


class QTrainer:
    def __init__(self, policy_dqn, target_dqn, enable_double_dqn, lr, gamma):
        self.lr = lr
        self.gamma = gamma
        self.policy_dqn = policy_dqn
        self.target_dqn = target_dqn
        target_dqn.load_state_dict(policy_dqn.state_dict())
        self.optimizer = optim.Adam(policy_dqn.parameters(), lr=self.lr)
        self.loss_fn = nn.MSELoss()

        self.enable_double_dqn = enable_double_dqn

    def train_step(self, state, action, reward, new_state, done):
        #states = torch.tensor(state, dtype=torch.float)
        #new_states = torch.tensor(new_states, dtype=torch.float)
        #actions = torch.tensor(action, dtype=torch.long).unsqueeze(0)
        #rewards = torch.tensor(reward, dtype=torch.float)
        if not (type(state) is list) and not (type(state) is tuple):
            state = [state]
            action = [action]
            reward = [reward]
            new_state = [new_state]
            done = [done]
        states = torch.stack(state)

        actions = torch.stack(action)

        new_states = torch.stack(new_state)

        rewards = torch.stack(reward)
        done = torch.tensor(done).float().to(device)
        '''if state.dim() == 1:
            state = state.unsqueeze(0)
            new_state = new_state.unsqueeze(0)
            action = action.unsqueeze(0)
            reward = reward.unsqueeze(0)
            done = torch.tensor([done], dtype=torch.float32, device=device)'''

        with torch.no_grad():
            if self.enable_double_dqn:
                #print(f"{new_states=}")
                best_actions_from_policy = self.policy_dqn(new_states).argmax(dim=1)

                target_q = rewards + (1-done) * self.gamma * \
                                self.target_dqn(new_states).gather(dim=1, index=best_actions_from_policy.unsqueeze(dim=1)).squeeze()
            else:
                # Calculate target Q values (expected returns)
                target_q = rewards + (1-done) * self.gamma * self.target_dqn(new_states).max(dim=1)[0]
                '''
                    target_dqn(new_states)  ==> tensor([[1,2,3],[4,5,6]])
                        .max(dim=1)         ==> torch.return_types.max(values=tensor([3,6]), indices=tensor([3, 0, 0, 1]))
                            [0]             ==> tensor([3,6])
                '''

        # Calcuate Q values from current policy
        #print(f"{actions=}")
        #print(actions.shape)
        #print(actions.dtype)
        #print(f"self.policy_dqn(states) {self.policy_dqn(states)}")
        current_q = self.policy_dqn(states).gather(dim=1, index=actions.unsqueeze(dim=1)).squeeze(1)
        '''
            policy_dqn(states)  ==> tensor([[1,2,3],[4,5,6]])
                actions.unsqueeze(dim=1)
                .gather(1, actions.unsqueeze(dim=1))  ==>
                    .squeeze()                    ==>
        '''

        # Compute loss
        #print(f"{current_q=}")
        #print(f"{target_q=}")
        loss = self.loss_fn(current_q, target_q)

        # Optimize the model (backpropagation)
        self.optimizer.zero_grad()  # Clear gradients
        loss.backward()             # Compute gradients
        self.optimizer.step()       # Update network parameters i.e. weights and biases



        '''if len(state.shape) == 1:
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

        self.optimizer.step()'''



