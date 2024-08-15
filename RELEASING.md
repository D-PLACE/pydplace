
Releasing pydplace
==================

- Change version to the new version number in
  - ``setup.cfg``
  - ``src/pydplace/__init__.py``

- Do platform test via ``tox``:
```shell
tox -r
```

- Make sure ``flake8`` passes (configuration in ``setup.cfg``):
```shell
flake8 src/
```
  
- Commit your change of the version number:
```shell
git commit -a -m "release <VERSION>"
```

- Create a release tag:
```shell
git tag -a v<VERSION> -m "<VERSION> release"
```

- Release to PyPI:
```shell
rm dist/*
python setup.py clean --all
python -m build -n
twine upload dist/*
```

- Push to GitHub:
```shell
git push origin
git push --tags origin
```

- Increment the version number and append `.dev0` to start the new development cycle:
  - `src/pydplace/__init__.py`
  - `setup.cfg`

- Commit/push the version change:
```shell
git commit -a -m "bump version for development"
git push origin
```
