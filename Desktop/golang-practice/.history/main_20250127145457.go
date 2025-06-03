package main

import (
    "fmt"
)

func fibonacci(n int) []int {
    if n < 2 {
        fmt.Println("Введите число от 2")
        return []int{}
    }

    slice := []int{1, 1}
    for i := 0; i < n; i++

}

func main() {
    fmt.Println("Введите число, чтобы увидеть для него ряд фибоначчи")

    var num int
    fmt.Scan(&num)
}