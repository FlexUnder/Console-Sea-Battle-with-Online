import random
import os
import time
import json
import platform
import netcode


def main():
    while True:
        connection, is_server = start_menu()
        if is_server:
            netcode.send_data(connection, 'Соединение установленно')
        else:
            time.sleep(1)
            print(netcode.listen_data(connection))
        start_game(connection, is_server)


def start_menu():
    clear_console()
    print('Добро пожаловать в морской бой, boy!\n')
    print('  Выбирете тип подключения (q чтобы выйти): ')
    print('\t1. Создать сервер')
    print('\t2. Подключиться (по ip)')
    is_server = False
    while True:
        choise = input('\t ~> ')
        if choise == '1':
            connection = netcode.start_server()
            is_server = True
            break
        if choise == '2':
            ip_server = input('Введите ip сервера: ')
            connection, success = netcode.connect_to_server(ip_server)
            if success:
                break
            else:
                print('\n  Выбирете тип подключения: ')
                print('\t1. Создать сервер')
                print('\t2. Подключиться (по ip)')
                continue
        if choise == 'q':
            print('Завершиение программы')
            exit()
        print('Некорректный ввод, введите 1/2')
    return connection, is_server


def start_game(connection, is_server):
    field = [['🌊'] * 10 for _ in range(10)]
    preparation_phase(field, connection)
    answer = netcode.listen_data(connection)
    print('Оба игрока готовы!')
    time.sleep(2)
    print('\n ...')
    time.sleep(3)
    shooting_phase(field, connection, is_server)


def preparation_phase(field, connection):  # Фаза подготовки
    def is_placement_valid():
        if (y1 == y2 and abs(x1 - x2) > 3) or (x1 == x2 and abs(y1 - y2) > 3) or (x1 != x2 and y1 != y2):
            return "Такой корабль разместить невозможно."
        if (y1 == y2 and ships_in_stock[abs(x1 - x2)] == 0) or (x1 == x2 and ships_in_stock[abs(y1 - y2)] == 0):
            return 'Корабли такой длины закончились'
        for x in range(min(x1, x2), max(x1, x2) + 1):
            for y in range(min(y1, y2), max(y1, y2) + 1):
                if (field[y][x] == '🚢') or (y != 9 and field[y + 1][x] == '🚢') or (y != 0 and field[y - 1][x] == '🚢') or \
                    (x != 9 and field[y][x + 1] == '🚢') or (x != 0 and field[y][x - 1] == '🚢') or \
                    ((x != 0 and y != 0) and field[y - 1][x - 1] == '🚢') or ((x != 9 and y != 9) and field[y + 1][x + 1] == '🚢') or \
                    ((x != 0 and y != 9) and field[y + 1][x - 1] == '🚢') or ((x != 9 and y != 0) and field[y - 1][x + 1] == '🚢'):
                    return "Корабли не могу пересекаться или стоять слишком блико друг к другу."
        return False
    # def delete():
    clear_console()
    ships_in_stock = {0: 4, 1: 3, 2: 2, 3: 1}
    while list(ships_in_stock.values()) != [0] * 4:
        clear_console()
        print('\n\t Фаза подготовки')
        print_field(field)
        print('Правила что мы делаем ээээх з еу потом напишем')
        print(f'\nУ вас в распопяжении: \n🚢 - {ships_in_stock[0]}\
              \n🚢🚢 - {ships_in_stock[1]}\n🚢🚢🚢 - {ships_in_stock[2]}\n🚢🚢🚢🚢 - {ships_in_stock[3]}')
        x1, y1 = input_coordinate('Введите координаты первой точки: ')
        if x1 == -1:
            connection.close()
            exit()
        x2, y2 = input_coordinate('Введите координаты второй точки: ')
        if x2 == -1:
            connection.close()
            exit()

        if is_placement_valid():
            print(is_placement_valid())
            print('Повторите ввод (нажмите Enter чтобы продолжить)')
            input()
            continue
        current_ships_parts = 0
        for x in range(10):
            for y in range(10):
                if (x1 <= x <= x2 or x2 <= x <= x1) and (y1 <= y <= y2 or y2 <= y <= y1):
                    current_ships_parts += 1
                    field[y][x] = '🚢'
        ships_in_stock[current_ships_parts - 1] -= 1
    clear_console()
    print('\t Фаза подготовки')
    print_field(field)
    print('\nВсе корабли размещены, ожидаем готовность второго игрока...')
    netcode.send_data(connection, 'ready|')


def shooting_phase(field, connection, is_server):  # Фаза выстрелов (хода)
    def is_hit(x, y, corpse):
        corpse.append((x, y))
        if (y != 9 and field[y + 1][x] == '🚢') or (y != 0 and field[y - 1][x] == '🚢')\
              or (y != 9 and field[y + 1][x] == '💥') or (y != 0 and field[y - 1][x] == '💥'):
            vertical = True
        elif (x != 9 and field[y][x + 1] == '🚢') or (x != 0 and field[y][x - 1] == '🚢')\
            or (x != 9 and field[y][x + 1] == '💥') or (x != 0 and field[y][x - 1] == '💥'):
            vertical = False
        else:
            corpse.append((x, y))
            return False
        if vertical:
            for i in range(1, 4):
                if y + i <= 9:
                    if field[y + i][x] == '🌊' or field[y + i][x] == '🌀':
                        break
                    corpse.append((x, y + i))
                    if field[y + i][x] == '🚢':
                        return True
            for i in range(1, 4):
                if y - i >= 0:
                    if field[y - i][x] == '🌊' or field[y - i][x] == '🌀':
                        break
                    corpse.append((x, y - i))
                    if field[y - i][x] == '🚢':
                        return True
        else:
            for i in range(1, 4):
                if x + i <= 9:
                    if field[y][x + i] == '🌊' or field[y][x + i] == '🌀':
                        break
                    corpse.append((x + i, y))
                    if field[y][x + i] == '🚢':
                        return True
            for i in range(1, 4):
                if x - i >= 0:
                    if field[y][x - i] == '🌊' or field[y][x - i] == '🌀':
                        break
                    corpse.append((x - i, y))
                    if field[y][x - i] == '🚢':
                        return True
        return False
    def is_shoot_invalid(x, y):
        if field_blind[y][x] != '🌫️':
            return '\nЭта область уже открыта, выберите другую точку для выстрела. Нажмите Enter, чтобы повторить'
    def open_water_area(x, y):
        for i in range(-1, 2):
            for j in range(-1, 2):
                if x + i > 9 or y + j > 9 or x + i < 0 or y + j < 0:
                    continue
                if field_blind[y + j][x + i] == '🌫️':
                    field_blind[y + j][x + i] = '🌊'
    def is_defeat():
        result = True
        for raw in field:
            if '🚢' in raw:
                result = False
        return result
    clear_console()
    if is_server:
        turn = random.choice(['server', 'client'])
        netcode.send_data(connection, turn)
    else:
        turn = netcode.listen_data(connection)
    field_blind = [['🌫️'] * 10 for _ in range(10)]
    winner = False
    while True:
        turn_swap = True
        if is_server and turn == 'server' or not is_server and turn == 'client':
            print('\t\tВаш ход')
            print_field(field_blind)
            x, y = input_coordinate('Введите координату выстрела: ')
            if x == -1 or y == -1:
                connection.close()
                exit()
            if is_shoot_invalid(x, y):
                print(is_shoot_invalid(x, y))
                input()
                clear_console()
                continue
            netcode.send_data(connection, f'{x},{y}')
            response = netcode.listen_data(connection)
            result = ''
            if response == 'hit':
                field_blind[y][x] = '💥'
                result = 'Точно в цель!'
                turn_swap = False
            elif response == 'miss':
                field_blind[y][x] = '💦'
                # time.sleep(0.25)
                field_blind[y][x] = '🌀'
                # time.sleep(0.25)
                field_blind[y][x] = '🌊'
                result = 'Промашка.'
            else:
                field_blind[y][x] = '💥'
                replace = json.loads(str(response).split('|')[1])
                # time.sleep(0.5)
                for coords in replace:
                    xd, yd = coords[0], coords[1]
                    field_blind[yd][xd] = '🛟'
                    open_water_area(xd, yd)
                    # time.sleep(0.1)
                result = 'Убил!'
                turn_swap = False
            clear_console()
            print('\t\tВаш ход')
            print_field(field_blind)
            print(result)
        else:
            print('\t Ход оппонента')
            print_field(field)
            x, y = list(map(int, str(netcode.listen_data(connection)).split(',')))
            result = ''
            if field[y][x] == '🚢':
                field[y][x] = '💥'
                replace = []
                if is_hit(x, y, replace):
                    netcode.send_data(connection, 'hit')
                    result = 'попал'
                else:
                    for coords in replace:
                        xd, yd = coords[0], coords[1]
                        field[yd][xd] = '🛟'
                        # time.sleep(0.1)
                    send_data(connection, 'destroyed|' + json.dumps(replace))
                    result = 'потопил судно'
                turn_swap = False
            elif field[y][x] == '🌊':
                field[y][x] = '💦'
                # time.sleep(0.5)
                field[y][x] = '🌀'
                netcode.send_data(connection, 'miss')
                result = 'промахнулся'
            clear_console()
            print('\t Ход оппонента')
            print_field(field)
            print(f'\nПротивник {result}!')
        time.sleep(2)
        if is_defeat():
            netcode.send_data(connection, 'ggwp')
            winner = False
            break
        else:
            netcode.send_data(connection, 'go next')
        game_status_answer = netcode.listen_data(connection)
        if game_status_answer == 'go next':
            if turn_swap:
                if turn == 'server':
                    turn = 'client'
                else:
                    turn = 'server'
            else:
                clear_console()
        if game_status_answer == 'ggwp':
            winner = True
            break
    if winner:
        print('\nПоздравляем! Все корабли противника уничтожены! Вы победили! 🥇🎉🤙')
    else:
        print('\n Ваши корабли уничтожены! Вы проиграли 😢😭😭')
    print('Игра завершина. Нажмите Enter')
    connection.close()
    input()


def input_coordinate(text):
    def is_input_invalid(_input):
        valid_alph = '0123456789abcdefghij'
        if len(_input) != 2:
            return 'Недопустимый ввод: введите букву и число (можно через пробел)'
        if _input[0].isdigit() == _input[1].isdigit():
            return 'Недопустимый ввод: введите точку координат (укажите строку (A-J) и столбец (1-10)))'
        if _input[0] not in valid_alph or _input[1] not in valid_alph:
            return 'Недопустимый ввод: введите точку координат (укажите строку (A-J) и столбец (1-10))'
        return False
    while True:
        input_first = list(input(text).replace('10', '0').replace(' ', '').lower())
        if input_first == ['q']:
            print('Матч будет завершен. Вы уверены что хотите выйти?[y/n]')
            if input('~>').lower() == 'y':
                return -1, -1
            else:
                continue
        if is_input_invalid(input_first):
            print(is_input_invalid(input_first))
            print('Повторите ввод (нажмите Enter чтобы продолжить)')
            input()
        else:
            break
    UNIDIF = 97
    if input_first[0].isdigit():
        x, y = int(input_first[0]) - 1, ord(input_first[1]) - UNIDIF
    else:
        x, y = int(input_first[1]) - 1, ord(input_first[0]) - UNIDIF
    if x == -1:
        x = 9
    return x, y


def print_field(field):  # вывод поля
    print('   ₁　​₂　₃　₄　₅　₆　₇　₈　₉ ₁₀')
    for i in range(10):
            a='ᴬᴮᶜᴰᴱᶠᴳᴴᴵᴶ'  # ᵃᵇᶜᵈᵉᶠᵍʰᴵʲ
            print(f' {a[i]}', '|'.join(field[i]))


def clear_console():
    system = platform.system().lower()
    if system == "windows":
        os.system('cls')
    else:
        os.system('clear')


if __name__ == '__main__':
    main()