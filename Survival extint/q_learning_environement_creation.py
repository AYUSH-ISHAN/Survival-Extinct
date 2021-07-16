import gym
import numpy as np
import matplotlib.pyplot as plt

env = gym.make("MountainCar-v0")

##############   go to the website and lookthe graphs and store their codes...
###########  And also see the video coded...  ## learns to grow larger and larger i.e. to go mmore farther from mean position.

LEARNING_RATE = 0.1
DISCOUNT = 0.95
EPISODES = 2000

SHOW_EVERY = 500   ## to be use to check whether it is working or not..

DISCRETE_OS_SIZE = [20]*len(env.observation_space.high)
discrete_os_win_size = (env.observation_space.high - env.observation_space.low)/DISCRETE_OS_SIZE   # discrete observation space window size

epsilon = 0.5    ### 0.5 but can put it as 1
START_EPSILON_DECAYING = 1
END_EPSILON_DECAYING = EPISODES // 2
epsilon_decay_value = epsilon/(END_EPSILON_DECAYING - START_EPSILON_DECAYING)

q_table  = np.random.uniform(low = 2, high = 0, size = (DISCRETE_OS_SIZE + [env.action_space.n]))  ## we have 20X20X3 table..

ep_rewards = []
aggr_ep_rewards = {'ep': [], 'avg': [], 'min': [], 'max': []}


def get_discrete_state(state):
    discrete_state = (state - env.observation_space.low) / discrete_os_win_size
    return tuple(discrete_state.astype(np.int))   ## check it..

for episode in range(EPISODES):

    episode_reward = 0

    if episode % SHOW_EVERY == 0:
        print(episode)
        render = True    #######   a little xchange at this place only...
    else:
        render = False
    discrete_state = get_discrete_state(env.reset())

    # print(discrete_state)
    # print(np.argmax(q_table[discrete_state]))   ## this is how we get the maximum value.

    Done = False
    while not Done:              #########   if we remove this epsilon part then it performs more greatly.
        if np.random.random() > epsilon:
            action = np.argmax(q_table[discrete_state])     # 0 - right, 1 - no action & 2 -  left
        else:
            action = np.random.randint(0, env.action_space.n)
        new_state, reward, done, _ = env.step(action)  # state is position and velocity

        episode_reward += reward

        new_discrete_state = get_discrete_state(new_state)
        if render:
            env.render()  ### it is like - to show the phenomens at render = True..

        if not Done:
            max_future_q = np.max(q_table[new_discrete_state])
            current_q = q_table[discrete_state + (action, )]
            new_q = (1-LEARNING_RATE) * current_q + LEARNING_RATE * (reward + DISCOUNT * max_future_q)
            q_table[discrete_state + (action, )] * new_q   # updating the state after we took that step,, [updating step]

        elif new_state[0] >= env.goal_position:
            print(f"We made it on episode {episode}")
            q_table[discrete_state + (action, )] = 0

        discrete_state = new_discrete_state

    if END_EPSILON_DECAYING >= episode >= START_EPSILON_DECAYING:
        epsilon -= epsilon_decay_value

    ep_rewards.append(episode_reward)

    if not episode % 10:
        np.save(f"qtables/{episode}-qtable.npy", q_table)  # saving the q_table.

    if not episode % SHOW_EVERY:
        average_reward = sum(ep_rewards[-SHOW_EVERY:])/len(ep_rewards[-SHOW_EVERY:])
        aggr_ep_rewards['ep'].append(episode)
        aggr_ep_rewards['avg'].append(average_reward)
        aggr_ep_rewards['min'].append(min(ep_rewards[-SHOW_EVERY:]))   # worst from the models
        aggr_ep_rewards['max'].append(max(ep_rewards[-SHOW_EVERY:]))    # the best from the models

        print(f"Episode: {episode} avg: {average_reward} min: {min(ep_rewards[-SHOW_EVERY:])} max: {max(ep_rewards[-SHOW_EVERY:])}")

env.close()

plt.plot(aggr_ep_rewards['ep'], aggr_ep_rewards['avg'], label = "avg")
plt.plot(aggr_ep_rewards['ep'], aggr_ep_rewards['min'], label = "min")
plt.plot(aggr_ep_rewards['ep'], aggr_ep_rewards['max'], label = "max")
plt.legend(loc = 4)
plt.show()