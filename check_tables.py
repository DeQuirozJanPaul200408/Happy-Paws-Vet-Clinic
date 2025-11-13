from db import query_one

try:
    result = query_one('SELECT COUNT(*) as count FROM otp_register')
    print(f'otp_register table has {result["count"]} rows')
except Exception as e:
    print(f'Error checking otp_register: {e}')

try:
    result2 = query_one('SELECT COUNT(*) as count FROM otp_login')
    print(f'otp_login table has {result2["count"]} rows')
except Exception as e:
    print(f'Error checking otp_login: {e}')

# Check recent entries
try:
    recent_register = query_one('SELECT * FROM otp_register ORDER BY created_at DESC LIMIT 1')
    if recent_register:
        print(f'Recent otp_register entry: {recent_register}')
    else:
        print('No entries in otp_register')
except Exception as e:
    print(f'Error checking recent otp_register: {e}')

try:
    recent_login = query_one('SELECT * FROM otp_login ORDER BY entered_at DESC LIMIT 1')
    if recent_login:
        print(f'Recent otp_login entry: {recent_login}')
    else:
        print('No entries in otp_login')
except Exception as e:
    print(f'Error checking recent otp_login: {e}')
