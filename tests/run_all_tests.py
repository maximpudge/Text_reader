"""
Главный скрипт для запуска всех тестов API и обработки текста.
"""
import importlib
import time
import os
import sys

def print_header(title, symbol='='):
    """Печать заголовка теста"""
    print("\n" + symbol * 80)
    print(f"{title}".center(80))
    print(symbol * 80 + "\n")

def print_result(name, success):
    """Печать результата теста"""
    if success:
        status = "✓ УСПЕШНО"
    else:
        status = "✗ НЕУДАЧНО"
    
    print(f"\n{name}: {status}\n")
    print("-" * 80)

def run_test_module(module_name):
    """Запускает тестовый модуль и возвращает результат"""
    try:
        print_header(f"Запуск тестов: {module_name}")
        module = importlib.import_module(f"tests.{module_name}")
        
        # Запускаем тесты, если есть функция main
        if hasattr(module, 'main'):
            start_time = time.time()
            module.main()
            end_time = time.time()
            duration = end_time - start_time
            print(f"\nВремя выполнения: {duration:.2f} секунд")
            return True
        else:
            print(f"Модуль {module_name} не содержит функции main")
            return False
    except Exception as e:
        print(f"Ошибка при запуске тестов из модуля {module_name}: {str(e)}")
        return False

def main():
    """Запуск всех тестов"""
    print_header("ЗАПУСК ВСЕХ ТЕСТОВ API ОБРАБОТКИ ТЕКСТА", "=")
    
    # Список тестовых модулей
    test_modules = [
        "test_manual",
        "test_api",
        "test_processing"
    ]
    
    # Определяем, запускать ли конкретные тесты
    if len(sys.argv) > 1:
        requested_tests = sys.argv[1:]
        test_modules = [m for m in test_modules if m in requested_tests or m.split('_')[-1] in requested_tests]
    
    # Запускаем тесты
    results = {}
    for module in test_modules:
        success = run_test_module(module)
        results[module] = success
    
    # Печатаем общие результаты
    print_header("РЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ", "=")
    all_success = True
    
    for module, success in results.items():
        print_result(module, success)
        if not success:
            all_success = False
    
    # Итоговый статус
    if all_success:
        print("\n✓ ВСЕ ТЕСТЫ УСПЕШНО ПРОЙДЕНЫ!")
    else:
        print("\n✗ ОБНАРУЖЕНЫ ОШИБКИ В ТЕСТАХ!")
    
    print("\nТестирование завершено!")
    return 0 if all_success else 1

if __name__ == "__main__":
    sys.exit(main()) 