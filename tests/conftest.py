from pathlib import Path

from pytest import fixture


images = [
    'boy-1.jpg',
    'construction-worker-1.jpeg',
    'girl-1.jpg',
    'girl-2.jpg',
    'hoodie-1.jpg',
    'man-1.jpeg',
    'woman-1.png',
    'woman-2.jpeg',
    'wonder-woman-1.jpeg',
]


@fixture(scope='session')
def examples() -> Path:
    """Return path to the `data` folder for test cases."""
    return Path(__file__).parent.parent / 'examples'


@fixture(scope='session')
def responses(examples) -> Path:
    """Return path to the `responses` folder for test cases."""
    responses = examples / 'responses'
    responses.mkdir(exist_ok=True)

    return responses
