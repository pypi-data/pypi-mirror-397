"""Test documentation."""

import os

import pytest

readme_snippets = []

if os.path.isfile(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../README.md")):
    with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "../README.md")) as f:
        for part in f.read().split("```python")[1:]:
            readme_snippets.append(part.split("```")[0].strip())


@pytest.mark.parametrize("snippet", readme_snippets)
def test_readme_snippets(snippet):
    exec(snippet)
