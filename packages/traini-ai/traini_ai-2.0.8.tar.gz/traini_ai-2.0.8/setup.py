"""
Setup configuration for Traini AI SDK
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# Read requirements
requirements = [
    'numpy>=1.21.0',
    'pillow>=9.0.0',
    'requests>=2.27.0',
    'torch>=1.12.0',
    'torchvision>=0.13.0',
    'openai>=1.0.0',
    'google-generativeai>=0.3.0',
    'anthropic>=0.8.0',
    'huggingface_hub>=0.20.0',
]

# Optional dependencies
extras_require = {
    'dev': [
        'pytest>=7.0.0',
        'pytest-cov>=3.0.0',
        'black>=22.0.0',
        'flake8>=4.0.0',
        'mypy>=0.950',
    ],
    'ml': [
        'torch>=1.12.0',
        'torchvision>=0.13.0',
        'opencv-python>=4.6.0',
    ],
    'audio': [
        'librosa>=0.9.0',
        'soundfile>=0.11.0',
        'pydub>=0.25.0',
    ],
    'all': [
        'torch>=1.12.0',
        'torchvision>=0.13.0',
        'opencv-python>=4.6.0',
        'librosa>=0.9.0',
        'soundfile>=0.11.0',
        'pydub>=0.25.0',
    ]
}

setup(
    name='traini-ai',
    version='2.0.8',
    author='Traini AI Team',
    author_email='support@traini.ai',
    description='Advanced AI-powered dog emotion detection and image analysis SDK',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/Traini-Inc/traini-sdk',
    packages=['traini_ai', 'traini_ai.models', 'traini_ai.modules', 'traini_ai.utils'],
    package_data={
        'traini_ai.models': ['*.json'],
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Scientific/Engineering :: Image Recognition',
        'Topic :: Multimedia :: Graphics :: Graphics Conversion',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
    install_requires=requirements,
    extras_require=extras_require,
    include_package_data=True,
    keywords='dog emotion detection ai image-analysis deep-learning multi-model gpt gemini claude pet-tech computer-vision',
    project_urls={
        'Bug Reports': 'https://github.com/Traini-Inc/traini-sdk/issues',
        'Source': 'https://github.com/Traini-Inc/traini-sdk',
        'Documentation': 'https://github.com/Traini-Inc/traini-sdk',
    },
)
