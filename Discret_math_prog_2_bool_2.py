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

def covers_minterm(implicant, minterm, num_vars):
    """Проверяет, покрывает ли импликант заданный минтерм."""
    val, mask = implicant
    # Импликант покрывает минтерм, если в значащих битах они совпадают
    return (minterm & mask) == (val & mask)

def build_coverage_table(prime_implicants, minterms, num_vars):
    """Строит таблицу покрытий."""
    table = []
    
    for i, impl in enumerate(prime_implicants):
        coverage = 0  # Битовая маска покрытых минтермов
        for j, m in enumerate(minterms):
            if covers_minterm(impl, m, num_vars):
                coverage |= (1 << j)  # Устанавливаем бит для этого минтерма
        table.append((impl, coverage))
    
    return table

def find_essential_implicants(table, minterms):
    """Находит ядерные (обязательные) импликанты."""
    num_minterms = len(minterms)
    essential = []
    used_indices = set()  # Храним уже добавленные индексы
    
    # Для каждого минтерма считаем, сколько импликантов его покрывают
    for j in range(num_minterms):
        covering_imps = []
        bit_mask = 1 << j
        
        for i, (impl, coverage) in enumerate(table):
            if coverage & bit_mask:
                covering_imps.append((i, impl))
        
        # Если минтерм покрыт только одним импликантом, тот ядерный
        if len(covering_imps) == 1:
            idx, impl = covering_imps[0]
            # Проверяем, не добавляли ли уже этот индекс
            if idx not in used_indices:
                used_indices.add(idx)
                # И проверяем, что это действительно уникальный импликант
                if (idx, impl) not in essential:
                    essential.append((idx, impl))
    
    return essential

def find_minimal_cover(table, minterms, essential_impls):
    """Находит минимальное покрытие жадным алгоритмом."""
    num_minterms = len(minterms)
    
    # Начинаем с ядерных импликантов (убираем дубликаты)
    selected_idxs = []
    for idx, _ in essential_impls:
        if idx not in selected_idxs:
            selected_idxs.append(idx)
    
    covered = 0
    
    # Покрытие от ядерных импликантов
    for idx in selected_idxs:
        _, coverage = table[idx]
        covered |= coverage
    
    # Если все покрыто, возвращаем результат
    if covered == (1 << num_minterms) - 1:
        return selected_idxs
    
    # Жадный выбор оставшихся импликантов
    remaining_imps = [i for i in range(len(table)) if i not in selected_idxs]
    
    while covered != (1 << num_minterms) - 1:
        best_idx = -1
        best_new_coverage = 0
        
        # Ищем импликант, который добавляет максимальное покрытие
        for i in remaining_imps:
            _, coverage = table[i]
            new_coverage = coverage & ~covered  # Биты, которые еще не покрыты
            new_coverage_count = count_ones(new_coverage)
            
            if new_coverage_count > best_new_coverage:
                best_new_coverage = new_coverage_count
                best_idx = i
        
        if best_idx == -1:
            break
            
        # Добавляем лучший импликант
        if best_idx not in selected_idxs:  # Проверка на дубликат
            selected_idxs.append(best_idx)
            _, coverage = table[best_idx]
            covered |= coverage
        
        # Удаляем из оставшихся, даже если не добавили (чтобы избежать бесконечного цикла)
        if best_idx in remaining_imps:
            remaining_imps.remove(best_idx)
    
    return selected_idxs

def print_implicant_bits(implicant, num_vars):
    """Выводит импликант в битовом формате."""
    val, mask = implicant
    for i in range(num_vars - 1, -1, -1):
        bit = 1 << i
        if mask & bit:
            print((val >> i) & 1, end="")
        else:
            print("-", end="")

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

def quine_mccluskey_full(minterms, num_vars, var_names):
    """Полная реализация метода Квайна-МакКласки."""
    print(f"МЕТОД КВАЙНА-МАККЛАСКИ ДЛЯ {num_vars} ПЕРЕМЕННЫХ")
    print("=" * 60) 
    # Шаг 1: Нахождение всех простых импликантов
    print("\n1. НАХОЖДЕНИЕ ВСЕХ ПРОСТЫХ ИМПЛИКАНТОВ")
    prime_implicants = find_prime_implicants(minterms, num_vars)
    
    print(f"Найдено {len(prime_implicants)} простых импликантов:")
    for i, impl in enumerate(prime_implicants):
        print(f"  P{i}: ", end="")
        print_implicant_bits(impl, num_vars)
        print("  →  ", end="")
        print_implicant_expr(impl, num_vars, var_names)
        print()
    
    # Шаг 2: Построение таблицы покрытий
    print("\n2. ТАБЛИЦА ПОКРЫТИЙ")
    table = build_coverage_table(prime_implicants, minterms, num_vars)
    # Выводим заголовок таблицы
    print("      ", end="")
    for m in minterms:
        print(f" m{m}", end="")
    print()
    
    for i, (impl, coverage) in enumerate(table):
        print(f"  P{i}: ", end="")
        for j in range(len(minterms)):
            if coverage & (1 << j):
                print("  ✓ ", end="")
            else:
                print("    ", end="")
        print("  ", end="")
        print_implicant_bits(impl, num_vars)
        print()
    
    # Шаг 3: Поиск ядерных импликантов
    print("\n3. ПОИСК ЯДЕРНЫХ ИМПЛИКАНТОВ")
    essential = find_essential_implicants(table, minterms)
    if essential:
        print(f"Найдено {len(essential)} ядерных импликантов:")
        for idx, impl in essential:
            print(f"  P{idx}: ", end="")
            print_implicant_bits(impl, num_vars)
            print("  →  ", end="")
            print_implicant_expr(impl, num_vars, var_names)
            print()
    else:
        print("Ядерные импликанты не найдены")
    
    # Шаг 4: Нахождение минимального покрытия
    print("\n4. МИНИМАЛЬНОЕ ПОКРЫТИЕ")
    minimal_idxs = find_minimal_cover(table, minterms, essential)
    # Убираем возможные дубликаты
    minimal_idxs = list(dict.fromkeys(minimal_idxs))
    minimal_impls = [prime_implicants[i] for i in minimal_idxs]
    
    print("Минимальное покрытие состоит из импликантов:", 
          ", ".join([f"P{i}" for i in minimal_idxs]))
    
    # Шаг 5: Результат
    print("\n5. РЕЗУЛЬТАТ")
    print("Сокращенная ДНФ (все простые импликанты):")
    print("F = ", end="")
    first = True
    for impl in prime_implicants:
        if not first:
            print(" + ", end="")
        print_implicant_expr(impl, num_vars, var_names)
        first = False
    print()
    
    print("\nМинимальная ДНФ:")
    print("F = ", end="")
    first = True
    for impl in minimal_impls:
        if not first:
            print(" + ", end="")
        print_implicant_expr(impl, num_vars, var_names)
        first = False
    
    print(f"\nВсего термов: {len(minimal_impls)}")
    return minimal_impls

def custom_example():
    num_vars = int(input("Введите количество переменных (2-5): "))
    if num_vars < 2 or num_vars > 5:
        print("Количество переменных должно быть от 2 до 5")
        return
        
    max_term = (1 << num_vars) - 1
        
    minterms_input = input(f"Введите минтермы через пробел (0-{max_term}): ")
    minterms = list(map(int, minterms_input.split()))
        
    if any(m < 0 or m > max_term for m in minterms):
        print(f"Минтермы должны быть в диапазоне 0-{max_term}")
        return
        
    var_names = []
    for i in range(num_vars):
        name = input(f"Введите имя переменной {i+1}: ")
        var_names.append(name)
        
    quine_mccluskey_full(minterms, num_vars, var_names)

def main():
    """Основная функция"""
    print("Полный метод Квайна-МакКваски")
    print("(с поиском минимальной ДНФ)")
    
    while True:
        print("\n" + "="*60)
        print("Меню:")
        print("  1. Ввести свои данные")
        print("  0. Выход")
        print("="*60)
        
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