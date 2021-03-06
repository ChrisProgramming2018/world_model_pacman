"""
Generating data from the CarRacing gym environment.
!!! DOES NOT WORK ON TITANIC, DO IT AT HOME, THEN SCP !!!
"""
import argparse
from os.path import join, exists
import gym
import numpy as np
from utils.misc import sample_continuous_policy
import gym_pacman
import cv2
import scipy.misc

def generate_data(rollouts, data_dir, noise_type): # pylint: disable=R0914
    """ Generates data """
    assert exists(data_dir), "The data directory does not exist..."

    env = gym.make("BerkeleyPacmanPO-v0")
    seq_len = 100

    for i in range(rollouts):
        env.reset("mediumClassic")
        # env.env.viewer.window.dispatch_events()
        if noise_type == 'brown':
            a_rollout = [env.action_space.sample() for _ in range(seq_len)]

        s_rollout = []
        r_rollout = []
        d_rollout = []
        t = 0
        while True:
            action = a_rollout[t]
            t += 1

            s, r, done, _ = env.step(action)
            
            s = scipy.misc.imresize(s, (64, 64, 3))
            s_rollout += [s]
            r_rollout += [r]
            d_rollout += [done]
            if done:
                env.reset("mediumClassic")
            if t == seq_len:
                print("> End of rollout {}, {} frames...".format(i, len(s_rollout)))
                np.savez(join(data_dir, 'rollout_{}'.format(i)),
                         observations=np.array(s_rollout),
                         rewards=np.array(r_rollout),
                         actions=np.array(a_rollout),
                         terminals=np.array(d_rollout))
                break

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--rollouts', type=int, default=10000, help="Number of rollouts")
    parser.add_argument('--dir', type=str, default=".", help="Where to place rollouts")
    parser.add_argument('--policy', type=str, choices=['white', 'brown'],
                        help='Noise type used for action sampling.',
                        default='brown')
    args = parser.parse_args()
    generate_data(args.rollouts, args.dir, args.policy)
