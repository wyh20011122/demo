
# Login and Registration System PRD

## Registration Requirements

1. Username cannot be empty.
2. Username length must be greater than 6 characters.
3. Password cannot be empty.
4. Password length must be greater than 8 characters.
5. Email format must be valid.
6. Confirm password must be the same as password.
7. If the username already exists, registration should fail.
8. If all information is valid, registration should succeed.

## Login Requirements

1. Username cannot be empty.
2. Password cannot be empty.
3. Users can log in only when username and password are correct.
4. If username or password is incorrect, login should fail.
5. After successful login, the system should return a welcome message.

## Intentional Bug

The PRD requires username length to be greater than 6 characters.
However, the backend intentionally does not validate username length.
