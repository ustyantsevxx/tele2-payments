import requests

auth_post_url = 'https://my.tele2.ru/auth/realms/tele2-b2c/protocol/openid-connect/token'
sms_post_url = 'https://tyumen.tele2.ru/api/validation/number/'
s = requests.Session()
number = '79044979272'


def send_sms_code():
    s.post(f'{sms_post_url}{number}', json={"sender": "Tele2"})


def save_token(token):
    f = open("token.txt", "w")
    f.write(token)
    f.close()


def read_token():
    try:
        f = open("token.txt", "r")
        token = f.readline()
        f.close()
        return token
    except IOError:
        return False


def get_token(sms_code):
    response = s.post(auth_post_url, {"client_id": "digital-suite-web-app",
                                      "grant_type": "password",
                                      "username": number,
                                      "password": sms_code,
                                      "password_type": "sms_code"})
    return response.json()['access_token']


def inject_token(token):
    s.headers.update({'Authorization': f'Bearer {token}'})


def refresh_token():
    send_sms_code()
    print('sms code for new token sent.')
    code = input('sms code: ')
    save_token(get_token(code))


def get_payments(from_date, to_date):
    token = read_token()
    if token:
        inject_token(token)
        response = s.get(
            f'https://my.tele2.ru/api/subscribers/{number}/payments',
            params={'fromDate': f'{from_date}T00:00:00+00:00',
                    'toDate': f'{to_date}T23:59:59+00:00'})
        if response.status_code != 200:
            print('token expired or invalid')
            refresh_token()
            return get_payments(from_date, to_date)
        else:
            return response.json()['data']
    else:
        print('file token.txt not found')
        refresh_token()


# date format: yyyy-mm-dd
payments = get_payments('2020-01-01', '2020-06-01')
print(payments)
