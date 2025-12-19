Official package used by all topdogalerts listeners

deployment steps:
1.) make and test changes
2.) increment version in pyproject.toml
3.) python3 -m build
4.) python3 -m twine upload dist/*