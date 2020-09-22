import setuptools

setuptools.setup(
    name="WF-CLI",
    version="0.0.1",
    author="JlChamaa",
    author_email="jlchamaa@gmail.com",
    description="A custom CLI Client for Workflowy",
    url="https://github.com/jlchamaa/wf_cli",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
