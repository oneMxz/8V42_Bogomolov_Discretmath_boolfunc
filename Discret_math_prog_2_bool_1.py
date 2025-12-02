import itertools

# Базовые битовые операции
def NOT(a): return ~a & 1
def AND(a, b): return a & b
def OR(a, b): return a | b
def XOR(a, b): return a ^ b

# Производные операции на основе базовых
def EQ(a, b): return NOT(XOR(a, b))               # Эквивалентность
def NOR(a, b): return NOT(OR(a, b))               # Стрелка Пирса
def NAND(a, b): return NOT(AND(a, b))             # Штрих Шеффера
def IMP(a, b): return OR(NOT(a), b)               # Импликация
def NIMP(a, b): return AND(a, NOT(b))             # Не импликация
def RIMP(a, b): return OR(a, NOT(b))              # Обратная импликация
def NRIMP(a, b): return AND(NOT(a), b)            # Не обратная импликация

def table_2vars(operation_name, operation_func):
    """Таблица истинности для двух переменных"""
    print(f"\n{operation_name}:")
    print(" p | q | Результат")
    print("-----------------")
    
    for p, q in itertools.product([0, 1], repeat=2):
        result = operation_func(p, q)
        print(f" {p} | {q} |     {result}")

def table_1var(operation_name, operation_func):
    """Таблица истинности для одной переменной"""
    print(f"\n{operation_name}:")
    print(" p | Результат")
    print("-------------")
    
    for p in [0, 1]:
        result = operation_func(p)
        print(f" {p} |     {result}")

def table_3vars():
    """Таблица истинности для трех переменных"""
    print(" a | b | c | Результат")
    print("----------------------")
    print("a&(b->c)")
    for a, b, c in itertools.product([0, 1], repeat=3):
        result = a&IMP(b,c)
        print(f" {a} | {b} | {c} |     {result}")

def main_simple():
    print("ПРОСТЫЕ ТАБЛИЦЫ ИСТИННОСТИ")
    print("=" * 50)
    print("Все вычисления через битовые операции")
    print("Нет строк для хранения промежуточных данных")
    print("=" * 50)
    
    # Таблицы для всех операторов
    table_2vars("Конъюнкция (p & q)", AND)
    table_2vars("Дизъюнкция (p | q)", OR)
    table_2vars("XOR (p ^ q)", XOR)
    table_2vars("Импликация (p → q)", IMP)
    table_2vars("Стрелка Пирса (p ↓ q)", NOR)
    table_2vars("Штрих Шеффера (p / q)", NAND)
    table_1var("Инверсия (!p)", NOT)
    table_2vars("Эквивалентность (p ~ q)", EQ)
    table_2vars("Не импликация (p ↛ q)", NIMP)
    table_2vars("Обратная импликация (p ← q)", RIMP)
    table_2vars("Не обратная импликация (p ↚ q)", NRIMP)
    table_3vars()

if __name__ == "__main__":
    main_simple()