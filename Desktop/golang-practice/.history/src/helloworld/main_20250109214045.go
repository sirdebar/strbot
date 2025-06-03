package main

import "fmt"

func main() {
    // Работа с массивом
    arr := [5]int{10, 20, 30, 40, 50}
    fmt.Println("Массив:", arr)

    // Создание среза из массива
    slice := arr[1:4] // Элементы с индексами 1, 2, 3
    fmt.Println("Срез из массива:", slice)

    // Добавление элементов к срезу
    slice = append(slice, 60, 70)
    fmt.Println("Срез после добавления:", slice)

    // Демонстрация изменения базового массива
    arr[2] = 100
    fmt.Println("Измененный массив:", arr)
    fmt.Println("Срез, связанный с массивом:", slice)

    // Создание нового среза
    newSlice := []int{1, 2, 3}
    fmt.Println("Новый срез:", newSlice)
}
