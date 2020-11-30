from collections import deque
from requests import get, post
from time import sleep

from sys import stderr, argv as args
from threading import Thread
from json import dumps as tojson, loads as fromjson

base_url = 'https://api.justswap.io/v2'
queue = deque(maxlen=50)

conf = {
    'minprice': 0,
    'maxprice': 30.0,
}

try:
    with open('conf.json') as f:
        custom = fromjson(f.read())
        for i in custom:
            conf[i] = custom[i]
except:
    print('Nãe existe conf.json na pasta atual, usando configuração padrão.',
          file=stderr)
print('configuração do script: ',
      tojson(conf, sort_keys=False, ident=4))

def _update_queue():
    global base_url, queue
    page = 1
    tryeds = 0

    while True:
        if tryeds == 10:
            print("Não foi possível se connectar a api, verifique sua conexão para que o script possa continuar",
                  file=stderr)
            sleep(10)
            tryeds = 0

        response = get(f'{base_url}/allpairs'
                       '?page_size=50'
                       f'&page_num={page}')

        if not response:
            tryeds += 1
            sleep(1)
            continue

        response = response.json()
        for item in response["data"]:
            queue.append(response["data"][item])

        page += 1

update_queue = Thread(target=_update_queue)
update_queue.start()
while True:
    try:
        for i in range(len(queue)):
            i = queue[0]
            i['price'] = float(i['price'])
            queue.popleft()

            if i['price'] >= conf["minprice"]\
                    and i['price'] <= conf['maxprice']:
                print(f'\033[1;32m', end="")
            else:
                print(f'\033[1;31m', end="")

            print(f'Name: {i["base_name"]}\n'
                  f'Coin: {i["quote_name"]}\n'
                  f'Price: {i["price"]}\n'
                  f'Id: {i["base_id"]}'
                  f'\033[00m\n')
    except Exception as e:
        print(e, 'Continuando execução em 1 segundo',
              sep="\n\n",
              file=stderr)
        update_queue._stop()
        update_queue.start()
        sleep(1)
        continue

