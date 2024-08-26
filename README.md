# openrct2_gym
This is a custom environment for [Gymnasium](https://gymnasium.farama.org/) that aims to train a RL agent to build great rollercoasters in OpenRCT2.

This project is heavily inspired by Dylan Eberts [neural_rct](https://dylanebert.com/neural_rct/) and Kevin Burke who held a [talk](https://www.youtube.com/watch?v=6mRFITUwCVU) which I thought was awesome.
That talk really wanted me to try it myself but I was just a mediocre python programmer with basic knowledge about neural networks. But now, thanks to LLM assisted coding I was able to create something that (kind of) works!

I started with the same method as Kevin Burke, reverse engineering the TD6-file format and create a python program that generates a rollercoaster in TD6-format. I was able to solve some of the issues Kevin had like collision detection by just creating a simple 3D-representation of the track in python.
But the real issue I then faced was trying to evaluate the ride to get its score. The game does this by just starting the ride, have the cart run through it and record all the values for speed, G-forces and such.
To do this in python I would first need to implement the whole physics engine from the game (the game even looks for scenery close to the track when evaluating the score) to get an accurate score in my python program.

So I started doing something different, I just made an UI wrapper around the OpenRCT2-game that clicks on the buttons in the UI and read the screen. This is slow but works as a proof of concept.

## Running the code
This code expects to run in a Linux environment with X-server for UI (Not Wayland) as this is what pyautogui supports.
The OpenRCT2-game needs to first be started and placed with its default window size in the top left corner for the button cordinates to be correct.
You then need to enter the track designer tool and choose just one rollercoster-type that you want to train on. The code is written for the standard Wooden Coster, not sure if it work for others.
Then just close all windows inside the game and start the train_rl_agent.py to start the training.

YES this is increadbly fragile and slow, but I have plans to improve it :)

## Training
This agent uses Stable Baselines3 and the PPO algorithm to train a network with two hidden layers of 128 neurons each for both the policy and value networks which I think should be enough for the complexity of this problem.
In the observation space we keep the track pieces used, the current height and direction, track total length, distance to start, last piece used and if the chain lift was used at all.
The goal currently is to try to make the agent understand that getting back to the start and compleating the track loop is very good and it should try to do that.

The plan is to have the agent make a complete loop and then start a test-run of the track and extract the score from the UI. This does not work yet as the text in the UI is so small that the image extraction-code fails to read it properly.
But even if it did I doubt this agent will ever learn to create a working rollercoaster, the training using the UI is just to slow and it probably takes a huge amount of training before the agent figures out how track design ties to ride score.
At best this current code will create an agent that can make complete track loops.

## Future work
Instead of using the UI it would be MUCH faster to work against an API.
Thanks to the great [Scripting API](https://github.com/OpenRCT2/OpenRCT2/blob/develop/distribution/scripting.md) in OpenRCT2 it would probably be possible to create a game plugin that exposes a API from the game that our training agent can use.
Then we could runt OpenRCT2 in headless mode without a UI and have the RL agent send commands and get feedback through the API instead which would be massively faster and less fragile then our current UI-clicking.
It would also make it possible to run multiple instances of OpenRCT2 at the same time in headless mode and multiply the training agent for even faster learning.
