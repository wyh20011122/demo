
# Automated Test Report

Generated Time: 2026-05-25 14:23:59.450042

## Summary

- Total Cases: 8
- Passed: 6
- Failed: 2
- Bugs: 2

## PRD Rules

- password length_greater_than 8\n- email valid_format contains @\n- confirm_password same_as_password True\n

## Test Results

### TC_REG_001 - Username shorter than required length\n- Expected Status: 400\n- Actual Status: 200\n- Result: FAIL\n- Response: {'message': 'Register success'}\n\n### TC_REG_002 - Username equals boundary length\n- Expected Status: 400\n- Actual Status: 200\n- Result: FAIL\n- Response: {'message': 'Register success'}\n\n### TC_REG_003 - Valid registration\n- Expected Status: 200\n- Actual Status: 200\n- Result: PASS\n- Response: {'message': 'Register success'}\n\n### TC_REG_004 - Password shorter than required length\n- Expected Status: 400\n- Actual Status: 400\n- Result: PASS\n- Response: {'error': 'Password must be longer than 8 characters'}\n\n### TC_REG_005 - Invalid email format\n- Expected Status: 400\n- Actual Status: 400\n- Result: PASS\n- Response: {'error': 'Invalid email format'}\n\n### TC_REG_006 - Confirm password does not match password\n- Expected Status: 400\n- Actual Status: 400\n- Result: PASS\n- Response: {'error': 'Confirm password does not match'}\n\n### TC_LOGIN_001 - Login with correct username and password\n- Expected Status: 200\n- Actual Status: 200\n- Result: PASS\n- Response: {'data': 'Welcome! You have successfully logged in.', 'message': 'Login success'}\n\n### TC_LOGIN_002 - Login with wrong password\n- Expected Status: 400\n- Actual Status: 400\n- Result: PASS\n- Response: {'error': 'Incorrect password'}\n\n

## Auto Generated Bugs

### BUG_TC_REG_001\n- Title: Requirement validation failed\n- Severity: HIGH\n- Priority: P1\n- Related Case: TC_REG_001\n- Description: Username shorter than required length\n- Expected: 400\n- Actual: 200\n- Status: OPEN\n\n### BUG_TC_REG_002\n- Title: Requirement validation failed\n- Severity: HIGH\n- Priority: P1\n- Related Case: TC_REG_002\n- Description: Username equals boundary length\n- Expected: 400\n- Actual: 200\n- Status: OPEN\n\n