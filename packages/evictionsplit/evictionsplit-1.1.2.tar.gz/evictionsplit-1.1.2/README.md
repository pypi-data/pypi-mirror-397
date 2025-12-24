# Eviction split

Alliance auth module dedicated to splitting the loot of an eviction between participants based on their participation time.

[![release](https://img.shields.io/pypi/v/evictionsplit?label=release)](https://pypi.org/project/evictionsplit/)
[![python](https://img.shields.io/pypi/pyversions/evictionsplit)](https://pypi.org/project/evictionsplit/)
[![django](https://img.shields.io/pypi/djversions/evictionsplit?label=django)](https://pypi.org/project/evictionsplit/)
[![license](https://img.shields.io/badge/license-MIT-green)](https://gitlab.com/r0kym/aa-evictionsplit/-/blob/master/LICENSE)

## Features:

- Create and manage evictions
- Apply to join an eviction
- Signal the current activity of members (standby and/or doorstopping)

### TODO:

- [ ] Enhance the signup for applicants specify what they bring to the eviction
- [x] Add information in the README for install
  - [x] Screenshots of the project also
- [x] Logging


### Screenshots

![](./images/view_eviction.png)

![](./images/admin_clocking.png)

## Installation

### Step 1 - Check prerequisites

Evictionsplit is a plugin for Alliance Auth.
If you don't have Alliance Auth running already, please install it first before proceeding.
(see the official [AA installation guide](https://allianceauth.readthedocs.io/en/latest/installation/auth/allianceauth/) for details)

### Step 2 - Install app

Make sure you are in the virtual environment (venv) of your Alliance Auth installation. Then install the newest release from PyPI:

```bash
pip install evictionsplit
```

### Step 3 - Configure Auth settings

Configure your Auth settings (`local.py`) as follows:

- Add `'evictionsplit',` to `INSTALLED_APPS`

### Step 4 - Finalize App installation

Run migrations & copy static files

```bash
python manage.py migrate
python manage.py collectstatic --noinput
```

Restart your supervisor services for Auth.

## Permissions

|      ID      |           Description           |                            Notes                            |
|:------------:|:-------------------------------:|:-----------------------------------------------------------:|
| basic_access |       Can access this app       |           All line members should have this role            |
|   manager    | Can create and manage evictions | Role to create/edit evictions and access archived evictions |
