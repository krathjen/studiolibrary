## Linting the code

### Installing Git hook:

* Install `flake8`:

```bash
pip install flake8
```

* Make sure you have it available trough `PATH` environment variable

* From the root of your StudioLibrary Git repository, run:

```bash
flake8 --install-hook git
cat [flake8] >> tox.ini
cat max-line-length=99 >> tox.ini
```

* Now you will have a list of problem cases in files when you commit. If you want to prevent bad commits at all, run:

```bash
git config --bool flake8.strict true
```