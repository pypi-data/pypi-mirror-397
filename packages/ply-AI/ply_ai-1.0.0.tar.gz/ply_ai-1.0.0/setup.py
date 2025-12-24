from setuptools import setup, find_packages

setup(
    name="ply-AI",
    version="1.0.0",
    description="Hardware-aware Triton accelerator library",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Zeng Jianrong",
    author_email="zeng@ply-ai.com",
    packages=find_packages(),
    install_requires=["torch", "triton"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
)
