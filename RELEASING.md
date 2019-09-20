
Releasing pydplace
==================

- Change version to the new version number in
  - ``setup.py``
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

- Release to PyPI (see https://github.com/di/markdown-description-example/issues/1#issuecomment-374474296):
```shell
python setup.py clean --all
rm dist/*
python setup.py sdist
twine upload dist/*
rm dist/*
python setup.py bdist_wheel
twine upload dist/*
```

- Push to GitHub:
```shell
git push origin
git push --tags origin
```

- Increment the version number and append `.dev0` to start the new development cycle:
  - `src/pydplace/__init__.py`
  - `setup.py`

- Commit/push the version change:
```shell
git commit -a -m "bump version for development"
git push origin
```
