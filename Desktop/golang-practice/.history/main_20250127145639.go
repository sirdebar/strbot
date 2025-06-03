package main

import (
	"fmt"
)

func fibonacci(n int) []int {
    // Проверка на минимальное значение
    if n < 2 {
        fmt.Println("Ошибка: число должно быть больше 2")
        return []int{}
    }

    // Инициализируем срез с первыми двумя элементами
    slice := []int{1, 1}

    // Генерируем остальные элементы (начиная с третьего)
    for i := 2; i < n; i++ {
        next := slice[i-1] + slice[i-2]
        slice = append(slice, next)
    }

    return slice
}

func main() {
    fmt.Print("Введите число элементов (>2): ")
    var num int
    fmt.Scan(&num)

    result := fibonacci(num)
    fmt.Println("Ряд Фибоначчи:", result)
}