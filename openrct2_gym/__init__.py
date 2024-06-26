from gymnasium.envs.registration import register

register(
    id='OpenRCT2-v0',
    entry_point='openrct2_gym.envs:OpenRCT2Env',
)
