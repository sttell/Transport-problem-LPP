# -*- coding: utf-8 -*-

from scipy.optimize import linprog
import time


def main():
    try:
        c, A_ub, b_ub, A_eq, b_eq = unpacking_task()
        start = time.time()
        solution = task_solution(c, A_ub, b_ub, A_eq, b_eq)
        stop = time.time()
        print_results(solution)
        print(f"Время: {stop - start}")
    except:
        print('''
Решение приостановлено автоматически.

Что-то пошло не так. Проверьте корректность введенных данных.
Подсказка: Возможно вы некорректно заполнили таблицу цен на поставки,
либо не соблюдали пробельные символы при введении данных.
Повторите попытку снова.        
        ''')


def unpacking_task():
    '''
    Function of packing the problem for supsequent solution
    using the SciPy package.
    :return:
        c: a vector of prices for the supply
        A_ub: matrix of the system relative to suppliers
        A_eq: matrix of the system relative to consumers
        b_ub: vector of capacities of suppliers
        b_eq: vector of consumer requests
    '''
    c, b_ub, b_eq, A_ub, A_eq, type_of_problem = input_data()
    print_unpack(c, A_ub, b_ub, A_eq, b_eq, type_of_problem)
    return c, A_ub, b_ub, A_eq, b_eq


def task_solution(c, A_ub, b_ub, A_eq, b_eq):
    '''
    Passing arguments to the SciPy solution function and getting the solution
    :param c: delivery price vector
    :param A_ub: system matrix relative to suppliers
    :param b_ub: supplier capacity vector
    :param A_eq: matrix of the system relative to consumers
    :param b_eq: consumer query vector
    :return: solution of the LPP(Linear Programming Problem)
    '''
    return linprog(c, A_ub, b_ub, A_eq, b_eq)


def print_results(solution):
    '''
    Registration of the results of the decision of the PO.
    :param solution: takes the decision of the scipy linprog()
    :return: None
    '''
    solution_data = list()
    solution_list = dict()

    # Unpacking the solution object received from the SciPy module
    for i in range(8):
        solution_data.append(solution.popitem())
    solution_data.reverse()

    # Selecting the necessary parameters
    _, VectorX = solution_data[0]
    for i in range(len(VectorX)):
        VectorX[i] = round(VectorX[i])
    solution_list["sv"] = VectorX  # Solution Vector
    _, solution_list['os'] = solution_data[1]  # Optimal Solution
    solution_list['os'] = round(solution_list['os'])
    _, solution_list['ss'] = solution_data[4]  # Solver status
    _, solution_list['msg'] = solution_data[5]  # Message
    _, solution_list['ni'] = solution_data[6]  # Number iteration
    _, solution_list['suc_s'] = solution_data[7]  # Success solve

    # Output information about the solution
    print(f"Задача решена успешно - {solution_list['suc_s']}")
    print(f'Вектор решений: {solution_list["sv"]}')
    print(f'Оптимальное решение(Минимум функции): {solution_list["os"]}')
    print(f"Статус решателя: {solution_list['ss']}")
    print(f'Сообщение менеджера решений: {solution_list["msg"]}')
    print(f'Количество итераций: {solution_list["ni"]}')


def input_data():
    '''
    This function is responsible for user input and primary packaging
    data in arrays that pass to the head function for further processing
    :return: list of transportation prices, supplier capacity,
    customer requests, the Matrix of the system regarding deliveries,
    Matrix of the system relative to consumers, task type
    '''
    # Input data of user
    print('Добро подаловать в систему решений транспортных задач.')
    cons = input('Введите мощности поставщиков: ')
    sup = input('Введите запросы потребителей: ')

    # Initialization of consumer and supplier lists and price matrix
    cons = [int(i) for i in cons.rstrip().lstrip().split()]
    sup = [int(i) for i in sup.rstrip().lstrip().split()]
    mtrx_price = []

    # Filling in the cost table
    print('Заполните таблицу цен на поставки:')
    print('''
    Замечание. Заполнение цен производится построчно,
    для одного поставщика в одной строке через пробел.
    Пример для трех заказчиков:
    Поставщик 1: 20 50 32 
    ''')

    # Filling in the price matrix
    for i in range(len(cons)):
        row = input(f'{i + 1}: ')
        mtrx_price.append([int(i) for i in row.rstrip().lstrip().split()])

    # This function checks whether the data entered by the user is correct.
    if checking_for_correctness(mtrx_price, sup, cons):
        return None

    # Defining the issue type and reducing it to an LPP
    type_of_problem = 'close'
    if sum(sup) == sum(cons):
        pass
    elif sum(sup) < sum(cons):
        type_of_problem = 'open_sup'
        sup.append(sum(cons) - sum(sup))
        for i in range(len(mtrx_price)):
            mtrx_price[i].append(0)
    else:
        type_of_problem = 'open_cons'
        cons.append(sum(sup) - sum(cons))
        mtrx_price.append([0 for _ in range(len(sup))])

    # Reducing the price matrix to a price vector
    c = []
    for i in mtrx_price:
        c += i

    A_ub = [[0 for _ in range(len(cons)*len(sup))] for _ in range(len(cons))]
    r = 0
    k = len(sup)
    # Making odds of the presence of elements in the matrix A_UB
    for i in range(len(cons)):
        A_ub[i][r:k] = [1 for _ in range(len(sup))]
        r += len(sup)
        k += len(sup)

    A_eq = [[0 for _ in range(len(cons) * len(sup))] for _ in range(len(sup))]
    # Making odds of the presence of elements in the matrix A_EQ
    r = 0
    for i in range(len(sup)):
        for _ in range(len(cons)):
            A_eq[i][r] = 1
            r += len(sup)
        r = i + 1

    print('-' * 80)
    print('-' * 80)

    return c, cons, sup, A_ub, A_eq, type_of_problem


def print_unpack(c, A_ub, b_ub, A_eq, b_eq, type_of_problem):
    '''
    The function outputs the results of packing a task entered by the user
    :param c: delivery price vector
    :param A_ub: system matrix relative to suppliers
    :param b_ub: supplier capacity vector
    :param A_eq: matrix of the system relative to consumers
    :param b_eq: consumer query vector
    :param type_of_problem: type of problem to solve
    :return:
    '''
    first_in_line = True  # Flag of the first element in the string
    fmt = ' x[{0}][{1}] '  # Format of output for non-zero elements of system

    # Объявление типа задачи
    if type_of_problem == 'close':
        print('Тип задачи: Закрытая транспортная задача.')
    elif type_of_problem == 'open_sup':
        print('Тип задачи: Открытая транспортная задача.')
        print('\n! Добавлен фиктивный поставщик !\n')
    else:
        print('Тип задачи: Открытая транспортная задача.')
        print('\n! Добавлен фиктивный потребитель !\n')

    # Output of the system and mathematical statement of the problem.
    print("Данные упакованы в решение задачи линейного программирования:")
    print("Математическая постановка задачи:\n")
    print("Система уравнений задачи:")
    for i in range(len(A_ub)):
        for j in range(len(A_ub[0])):
            if A_ub[i][j] == 0:
                print('', end='')
            elif first_in_line:
                first_in_line = False
                print(fmt.format(i + 1, j + 1), end='')
            else:
                print((' + ' + fmt).format(i + 1, j + 1), end='')
        print(f' = {b_ub[i]}')
        first_in_line = True
    for i in range(len(A_eq)):
        for j in range(len(A_eq[0])):
            if A_eq[i][j] == 0:
                print('', end='')
            elif first_in_line:
                first_in_line = False
                print(fmt.format(i + 1, j + 1), end='')
            else:
                print((' + ' + fmt).format(i + 1, j + 1), end='')
        print(f' = {b_eq[i]}')
        first_in_line = True
    print('')

    # Output of the target function.
    ot_sett = max(c)
    print('Целевая функция задачи: ')
    print(f'F(X) = ', end='')
    fmt1 = '{0:>' + str(len(str(ot_sett))) + '}*x[{1}]'
    for i in range(len(c)):
        if i == 0:
            print(fmt1.format(c[0], 1), end='')
        elif c[i] == 0:
            print('', end='')
        else:
            print(('+' + fmt1).format(c[i], i+1), end='')
    print(' ---> min')

    print('-' * 80)
    print('-' * 80)


def checking_for_correctness(mtrx, sup, cons):
    '''
    This function checks whether the data entered by the user is correct.
    :param mtrx: Price matrix
    :param sup: supplier list
    :param cons: consumer list
    :return: flag (True/False) True - Stop programm
    default flag - False
    '''
    for row in mtrx:
        if len(row) != len(sup):
            return True
    if len(mtrx) != len(cons):
        return True
    return False


main()
