import socket
import ifaddr
import time
import ipaddress
import main


def send_data(connection, data):
    try:
        connection.sendall(data.encode('utf-8'))
    except ConnectionResetError:
        print('Соединение разорвано. Возможно противник покинул бой. Нажмите Enter')
        connection.close()
        input()
        main.main()
    except ConnectionAbortedError:
        print('Соединение разорвано. Возможно противник покинул бой. Нажмите Enter')
        connection.close()
        input()
        main.main()


def listen_data(connection):
    try:
        data = connection.recv(1024)
        return data.decode("utf-8")
    except ConnectionResetError:
        print('Ваш противник вышел!. Нажмите Enter')
        connection.close()
        input()
        main.main()
    except ConnectionAbortedError:
        print('Ваш противник вышел!. Нажмите Enter')
        connection.close()
        input()
        main.main()


def start_server():
    local_ip, hamachi_ip, is_hamachi_found = get_all_local_ips(True)
    _socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    _socket.bind(('0.0.0.0', 7878))
    _socket.listen(5)
    print("Сервер запущен")
    print('Ваш ip: ' + local_ip + is_hamachi_found * f'\nВаш Hamachi ip: {hamachi_ip}')
    connection, address = _socket.accept()
    ip, _ = address
    try:
        print('Подсоединен:', socket.gethostbyaddr(ip)[0].split('.')[0]) # socket.getfqdn(ip).split('.')[0] вызывает ошибку
    except socket.herror:
        print('Подсоединен:', ip)
    time.sleep(3)
    return connection


def connect_to_server(server_ip):
    print('Соединение...')
    server = (server_ip, 7878)
    connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        connection.connect(server)
        print('\nСервер найден! Подключен к:', socket.gethostbyaddr(server_ip)[0].split('.')[0]) # socket.getfqdn(ip).split('.')[0] вызывает ошибку
    except socket.herror:
        print('\nСервер найден! Подключен к:', server_ip)
    except socket.gaierror:
        print('Некорректный ip адрес')
        return None, False
    except TimeoutError:
        print('Cервер не найден. Убедитесь в правильности написания адреса. Если подключаетесь по Hamachi, то убедитесь в том что Hamachi включен')
        return None, False
    except ConnectionRefusedError:
        print('Компьютер найден, но соединение было отвергнуто. Проверьте запущен ли сервер, проверьте настройки firewall')
        return None, False
    time.sleep(3)
    return connection, True


def get_all_local_ips(prefer_hamachi=True):
    ham_ips = find_hamachi_ips()
    if prefer_hamachi and ham_ips:
        return get_default_local_ip(), ham_ips[0], True
    return get_default_local_ip(), None, False


def get_default_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    local_ip = s.getsockname()[0]
    s.close()
    return local_ip


def find_hamachi_ips():
    hamachi_net = ipaddress.ip_network("25.0.0.0/8")
    result = []
    for adapter in ifaddr.get_adapters():
        name = (adapter.nice_name or "").lower()
        name_hint = any(tok in name for tok in ("hamachi", "logmein", "ham"))
        for ipinfo in adapter.ips:
            addr = ipinfo.ip
            if isinstance(addr, tuple):
                addr = addr[0]
            try:
                ip_obj = ipaddress.ip_address(addr)
            except ValueError:
                continue
            if ip_obj.version == 4 and ip_obj in hamachi_net:
                result.append(str(ip_obj))
            elif ip_obj.version == 4 and name_hint:
                result.append(str(ip_obj))
    return list(dict.fromkeys(result))
