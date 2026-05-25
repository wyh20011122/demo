
# Login and Registration System PRD

## 1. Project Background

This project is a simple login and registration system used as the system under test.
The purpose is to verify whether an automated testing plugin can analyze PRD requirements,
generate test cases, execute tests, generate reports, and automatically create bugs.

## 2. Registration Requirements

1. Username cannot be empty.
2. Username length must be greater than 6 characters.
3. Username should not contain SQL injection patterns.
4. Username should not contain script tags.
5. Password cannot be empty.
6. Password length must be greater than 8 characters.
7. Email format must be valid.
8. Confirm password must be the same as password.
9. If the username already exists, registration should fail.
10. If all information is valid, registration should succeed.

## 3. Login Requirements

1. Username cannot be empty.
2. Password cannot be empty.
3. Users can log in only when username and password are correct.
4. If username or password is incorrect, login should fail.
5. If the user does not exist, login should fail.
6. After successful login, the system should return a welcome message.

## 4. Intentional Bug

The PRD requires username length to be greater than 6 characters.

However, the backend intentionally does not validate username length during registration.

This means usernames such as "abc" and "abcdef" can still be registered successfully.

This intentional bug is used to demonstrate automated PRD-based testing and bug generation.
