# PolarBear API documentation

## General Usage Information

Endpoints are authenticated with HTTP Basic auth, with one of two
types of accounts:

- **Node accounts**: accounts for specific nodes, can generally access
  anything, and act on behalf of their users. support for these will
  not be fully complete until part 2. these can be created like so

  ```
  $ ./manage.py createnode
  ```

- **Ordinary author accounts**: these have the same permissions that
    they have in the browser interface. they can be created only with
    the browser interface.


## Post Management

## Friend Management

## Other