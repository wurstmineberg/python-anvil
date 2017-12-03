#!/usr/bin/env python

import setuptools

setuptools.setup(
    name='mcanvil',
    description="A parser for Minecraft's Anvil world format",
    author='Wurstmineberg',
    author_email='mail@wurstmineberg.de',
    packages=['mcanvil'],
    install_requires=[
        'nbt'
    ]
)
