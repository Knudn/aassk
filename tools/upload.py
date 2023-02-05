import requests


def upload(ip,file_path):
    print()
    headers = {
    'Host': '{0}:5000'.format(ip),
    # 'Content-Length': '108',
    'Cache-Control': 'max-age=0',
    'Upgrade-Insecure-Requests': '1',
    'Origin': 'http://{0}:5000'.format(ip),
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.5414.120 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Referer': 'http://{0}:5000/setup'.format(ip),
    # 'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'en-US,en;q=0.9',
    'Connection': 'close',
    }
    print('http://{0}:8000/{1}'.format(ip,file_path))
    data = {
        'upload_link': 'http://{0}:8000/{1}'.format(ip,file_path),
    }

    response = requests.post('http://{0}:5000/upload_link'.format(ip), headers=headers, data=data, verify=False)

def remove(ip,file_path):

    headers = {
    'Host': '{0}:5000'.format(ip),
    # 'Content-Length': '108',
    'Cache-Control': 'max-age=0',
    'Upgrade-Insecure-Requests': '1',
    'Origin': 'http://{0}:5000'.format(ip),
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.5414.120 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Referer': 'http://{0}:5000/setup'.format(ip),
    # 'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'en-US,en;q=0.9',
    'Connection': 'close',
    }


    data = {
        'content_id': 'http://{0}:8000/{1}'.format(ip,file_path),
    }

    response = requests.post('http://{0}:5000/remove_content'.format(ip), headers=headers, data=data, verify=False)
