from collections import deque
#from random import random
import random

from icecream import ic

from config_game import MAX_MEMORY, BATCH_SIZE, LR, device, flag_train_gun
from config_neural_loader import config_neural
from model_q_torch import QTrainer

import torch

import torch.nn.functional as F

class Agent:

    def __init__(self, model, target_model, enable_double_dqn):


        self.n_games = 0
        self.epsilon = 0
        self.gamma = config_neural.AGENT.gamma #0.9
        self.memory = deque(maxlen=MAX_MEMORY) # popleft()
        self.model = model
        #self.model = torch.compile(self.model)

        self.target_model = target_model
        #self.target_model = torch.compile(self.target_model)
        self.trainer = QTrainer(self.model, self.target_model, enable_double_dqn, lr=LR, gamma=self.gamma)

        self.flag_training = True

        self.acts = {
            config_neural.GET_ACTION.name: self.get_action,
            config_neural.GET_ACTION_RANDOM.name: self.get_action_random,
            config_neural.GET_ACTION_LITE_RANDOM.name: self.get_action_lite_random,
            config_neural.GET_ACTION_STAHIOHASTIC.name: self.get_action_stahiohastic,
            config_neural.GET_ACTION_EPSILON.name: self.get_action_epsilon,
        }

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE)
        else:
            mini_sample = self.memory
        #print(f"{mini_sample=}")

        #try:
        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)
        #self.memory.clear()
       # except:
        #    print("ни одного попадания")


    def train_short_memory(self, state, action_ind, reward, next_state, done):
        '''action_ind = action.index(1)
        state = torch.tensor(state, dtype=torch.float)#.unsqueeze(dim=0)
        action_ind = torch.tensor(action_ind, dtype=torch.int64)#.unsqueeze(dim=0)
        reward = torch.tensor(reward, dtype=torch.float)#.unsqueeze(dim=0)
        next_state = torch.tensor(next_state, dtype=torch.float)#.unsqueeze(dim=0)
        done = torch.tensor(done).float()'''

        self.trainer.train_step(state, action_ind, reward, next_state, done)

    def get_action(self, state,  *args):
        final_move = [0] * self.model.output.out_features
        with torch.no_grad():
            state0 = torch.tensor(state, dtype=torch.float, device=device)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            final_move[move] = 1
        return final_move




    def get_action_random(self, state, *args):
        K_len_learn = config_neural.GET_ACTION_RANDOM.K_len_learn
        proc_rand = config_neural.GET_ACTION_RANDOM.proc_rand
        self.epsilon = proc_rand*K_len_learn - self.n_games
        final_move = [0] * self.model.output.out_features
        if random.randint(0, 100*K_len_learn) < self.epsilon and self.flag_training:
            move = random.randint(0, 3)
            final_move[move] = 1

        else:
            return self.get_action(state)

        return final_move

    def get_action_lite_random(self, state, *args):
        final_move = [0] * self.model.output.out_features
        proc_rand = config_neural.GET_ACTION_LITE_RANDOM.proc_rand


        if random.randint(1, 100//proc_rand) == self.flag_training:#self.flag_rand_stachiochastic#1
            move = random.randint(0, self.model.output.out_features-1)
            final_move[move] = 1
        else:
            return self.get_action(state)

        return final_move
    def get_action_stahiohastic(self, state, *args):
        final_move = [0] * self.model.output.out_features
        #print(f"{final_move=}")

        temperature = config_neural.GET_ACTION_STAHIOHASTIC.temperature

        #print("=======================")
        #print(f"object: {self.__class__.__name__}")
        state0 = torch.tensor(state, dtype=torch.float, device=device)
        #state0 = state
        #print(f"{state=}")
        prediction = self.model(state0)
        #print(f"{prediction[0]}")
        probs = F.softmax(prediction[0] / temperature, dim=0)
        #print(f"{probs=}")
        move = torch.multinomial(probs, num_samples=1).item()
        #print(f"{move=}")
        final_move[move] = 1
        #print(probs)
        #print("=======================")

        return final_move

    def get_action_epsilon(self, state, epsilon):
        final_move = [0] * self.model.output.out_features



        if random.random() < epsilon:  # self.flag_rand_stachiochastic#1
            move = random.randint(0, 3+flag_train_gun)
            final_move[move] = 1
        else:
            return self.get_action(state)

        return final_move
