from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name='verifastscore',
    version='0.1.5',
    description='Fast, end-to-end factuality evaluation for long-form LLM responses.',
    author='Rishanth Rajendhran',
    author_email='rishanth@umd.edu',
    url='https://github.com/rishanthrajendhran/verifastscore',
    license='Apache 2.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'torch',
        'transformers',
        'spacy',
        'tqdm',
        'regex',
        'requests',
    ],
    entry_points={
        'console_scripts': [
            'verifastscore=verifastscore.verifastscore:main',
        ]
    },
    python_requires='>=3.9',
    long_description=long_description,
    long_description_content_type="text/markdown",
)
