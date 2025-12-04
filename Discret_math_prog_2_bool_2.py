def count_ones(num):
    """Подсчет единиц в двоичном представлении числа."""
    cnt = 0
    while num:
        cnt += num & 1
        num >>= 1
    return cnt

def can_combine(impl1, impl2):
    """
    Проверяет, можно ли склеить два импликанта.
    Возвращает (можно_ли, позиция_различия) или (False, 0).
    """
    val1, mask1 = impl1
    val2, mask2 = impl2
    
    # Маски должны совпадать
    if mask1 != mask2:
        return False, 0
    
    # Находим различающиеся биты
    diff = (val1 ^ val2) & mask1
    
    # Должен различаться ровно один бит
    if diff and (diff & (diff - 1)) == 0:
        return True, diff
    return False, 0

def combine_implicants(impl1, impl2, diff_bit):
    """Склеивает два импликанта, убирая различающийся бит."""
    val1, mask1 = impl1
    # Новая маска: убираем различающийся бит
    new_mask = mask1 & ~diff_bit
    # Новое значение: сохраняем общие биты
    new_val = val1 & new_mask
    return (new_val, new_mask)

def find_prime_implicants(minterms, num_vars):
    """Нахождение всех простых импликантов."""
    # Инициализация: каждый минтерм - полный вектор
    full_mask = (1 << num_vars) - 1
    current_set = [(m, full_mask) for m in minterms]
    prime_implicants = []
    
    while current_set:
        # Сортируем по количеству единиц
        current_set.sort(key=lambda x: count_ones(x[0]))
        
        # Создаем группы по количеству единиц
        groups = {}
        for val, mask in current_set:
            weight = count_ones(val & mask)
            if weight not in groups:
                groups[weight] = []
            groups[weight].append((val, mask))
        
        # Списки для следующей итерации и неиспользованных импликантов
        next_set = []
        used = [0] * len(current_set)
        
        # Проходим по всем парам соседних групп
        sorted_weights = sorted(groups.keys())
        
        for i in range(len(sorted_weights) - 1):
            w1 = sorted_weights[i]
            w2 = sorted_weights[i + 1]
            
            # Проверяем только соседние по весу группы
            if w2 - w1 != 1:
                continue
                
            for impl1 in groups[w1]:
                for impl2 in groups[w2]:
                    can_comb, diff_bit = can_combine(impl1, impl2)
                    if can_comb:
                        # Находим индексы в current_set
                        idx1 = current_set.index(impl1)
                        idx2 = current_set.index(impl2)
                        used[idx1] = 1
                        used[idx2] = 1
                        
                        # Создаем новый импликант
                        new_impl = combine_implicants(impl1, impl2, diff_bit)
                        
                        # Добавляем, если еще нет
                        if new_impl not in next_set:
                            next_set.append(new_impl)
        
        # Добавляем неиспользованные импликанты в простые
        for i, impl in enumerate(current_set):
            if not used[i] and impl not in prime_implicants:
                prime_implicants.append(impl)
        
        # Переходим к следующей итерации
        current_set = next_set
    
    return prime_implicants

def print_implicant_expr(implicant, num_vars, var_names):
    """Выводит импликант в виде булева выражения."""
    val, mask = implicant
    first = True
    
    for i in range(num_vars - 1, -1, -1):
        bit = 1 << i
        if mask & bit:
            var_idx = num_vars - 1 - i
            if not first:
                print("·", end="")
            
            bit_val = (val >> i) & 1
            if bit_val:
                print(var_names[var_idx], end="")
            else:
                print("¬", var_names[var_idx], sep="", end="")
            first = False
    
    if not first:
        print("", end="")
    else:
        print("1", end="")

def quine_mccluskey_simplified(minterms, num_vars, var_names):
    """Упрощенная реализация метода Квайна-МакКласки - только сокращенная ДНФ."""
    # Шаг 1: Нахождение всех простых импликантов (сокращенная ДНФ)
    print("\n" + "="*50)
    print(f"СОКРАЩЕННАЯ ДНФ для {num_vars} переменных")
    print("="*50)
    
    prime_implicants = find_prime_implicants(minterms, num_vars)
    
    if not prime_implicants:
        print("F = 0")
        return []
    
    # Проверяем, покрывает ли один импликант все минтермы
    if len(prime_implicants) == 1:
        val, mask = prime_implicants[0]
        # Если маска пустая (все биты прочерки)
        if mask == 0:
            print("F = 1")
            return prime_implicants
    
    print("F = ", end="")
    first = True
    for impl in prime_implicants:
        if not first:
            print(" + ", end="")
        print_implicant_expr(impl, num_vars, var_names)
        first = False
    
    print(f"\n\nВсего термов в сокращенной ДНФ: {len(prime_implicants)}")
    return prime_implicants

def custom_example():
    """Ввод пользовательских данных."""
    num_vars = int(input("Введите количество переменных (2-5): "))
    if num_vars < 2 or num_vars > 5:
        print("Количество переменных должно быть от 2 до 5")
        return
        
    max_term = (1 << num_vars) - 1
        
    minterms_input = input(f"Введите минтермы через пробел (0-{max_term}): ")
    minterms = list(map(int, minterms_input.split()))
    
    # Удаляем дубликаты и сортируем
    minterms = sorted(set(minterms))
        
    if any(m < 0 or m > max_term for m in minterms):
        print(f"Минтермы должны быть в диапазоне 0-{max_term}")
        return
    
    # Проверяем все возможные минтермы
    all_minterms = set(range(max_term + 1))
    if set(minterms) == all_minterms:
        print("\n" + "="*50)
        print(f"СОКРАЩЕННАЯ ДНФ для {num_vars} переменных")
        print("="*50)
        print("F = 1")
        return
        
    var_names = []
    for i in range(num_vars):
        name = input(f"Введите имя переменной {i+1}: ")
        var_names.append(name)
        
    quine_mccluskey_simplified(minterms, num_vars, var_names)

def main():
    print("Метод Квайна-МакКласки")
    while True:
        print("Меню:")
        print("  1. Ввести свои данные")
        print("  0. Выход")
        choice = input("Выберите вариант: ").strip()
        if choice == "1":
            custom_example()
        elif choice == "0":
            print("Выход из программы.")
            break
        else:
            print("Неверный выбор. Попробуйте еще раз.")

if __name__ == "__main__":
    main()