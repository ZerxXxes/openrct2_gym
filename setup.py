from setuptools import setup, find_packages

setup(
    name='openrct2_gym',
    version='0.0.1',
    packages=find_packages(),
    install_requires=[
        'gymnasium',
        'numpy',
        'pyautogui',
        'pillow'
    ],
)

