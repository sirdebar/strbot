package main

import (
    "fmt"
)

func fibonacci(n int) []int {
    if n < 2 {
        fmt.Println("")
        return []int{}
    }
}

func main() {
    fmt.Println("Введите число, чтобы увидеть для него ряд фибоначчи")

    var num int
    fmt.Scan(&num)
}