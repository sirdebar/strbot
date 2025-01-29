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
    for i := 2; i < n; i++{
        next := slice[i-1] + slice[i+1]
        slice = append(slice, next)
    }

    return slice

}

func main() {
    fmt.Println("Введите число, чтобы увидеть для него ряд фибоначчи")
    var num int
    fmt.Scan(&num)

    res := fibonacci(num)
    fmt.Println(res)
}