# CMPUT404-project
[![CircleCI](https://circleci.com/gh/Petelliott/CMPUT404-project.svg?style=svg)](https://circleci.com/gh/Petelliott/CMPUT404-project)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)


[API documentation](API.md)

[Admin documentation](Admin.md)

## Getting Started:
### Setup:
```
virtualenv venv --python=python3
source venv/bin/activate
pip install -r requirements.txt
```

***Note: If you are using macOS, you might need to install libmagic.***
```
brew install libmagic
```

### Run:
```
python manage.py runserver
```

### demo accounts

on https://cmput404w20t06.herokuapp.com/ there are the following
approved demo accounts (username/password) : `demo/demo`,
`demo2/demo2`, `demo3/demo3`

### configuring github integration

in order to not get rate limited by github, you need to create an
oauth app and set the `GITHUB_AUTH` environment variable to
`client_id:client_secret`.