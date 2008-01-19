from setuptools import find_packages, setup

setup(
    name='ticket2rtm', version='0.1',
    packages=find_packages(exclude=['*.tests*']),
    entry_points = """
        [trac.plugins]
        ticket2rtm = ticket2rtm
    """,
)
