// Однострочный комментарий: основной файл программы

#include <iostream> // Подключение стандартной библиотеки ввода-вывода

#define PI 3.14159 // Определение макроса

/*
    Многострочный комментарий:
    Пример программы на C++
    Содержит основные синтаксические элементы.
*/

int main() { // Ключевое слово int, main - идентификатор, { - разделитель
    // Объявление переменных
    int a = 42;              // Целочисленный литерал
    double b = 2.718;        // Вещественный литерал
    float c = 1.5e-5;        // Литерал в экспоненциальной нотации
    char d = 'A';            // Символьный литерал
    bool isValid = true;     // Логический литерал
    std::string greeting = "Hello, World!"; // Строковой литерал

    // Операторы: арифметические, логические, присваивания
    int sum = a + static_cast<int>(b); // Оператор приведения типов (static_cast), оператор сложения (+)
    bool check = (a > 0) && (b < 5);   // Операторы сравнения (>), (<), логический оператор (&&)

    // Управляющие операторы: условные операторы и циклы
    if (check) {  // Ключевое слово if, разделитель (, )
        std::cout << greeting << " Sum: " << sum << std::endl; // Операторы вывода, литералы и разделители
    } else { // Ключевое слово else
        std::cout << "Condition is false." << std::endl; // Строковой литерал
    }

    for (int i = 0; i < 5; ++i) { // Цикл for, операторы ++ и <
        std::cout << "Loop iteration: " << i << std::endl; // Строковой и числовой литерал, оператор вывода
    }

    // Оператор switch и перечисление
    enum Color { RED, GREEN, BLUE }; // Перечисление с идентификаторами
    Color myColor = GREEN; // Инициализация переменной перечисления
    switch (myColor) { // Оператор switch
        case RED: // Метка case
            std::cout << "Red color" << std::endl;
            break; // Оператор break
        case GREEN:
            std::cout << "Green color" << std::endl;
            break;
        case BLUE:
            std::cout << "Blue color" << std::endl;
            break;
        default: // Метка default
            std::cout << "Unknown color" << std::endl;
    }

    // Указатели и операции с указателями
    int* p = &a; // Оператор взятия адреса &, указатель
    *p = 10; // Оператор разыменования *

    // Строковый литерал с экранированными символами
    std::cout << "File path: C:\\Program Files\\MyApp" << std::endl; 

    return 0; // Ключевое слово return
}