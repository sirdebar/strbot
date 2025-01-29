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
        next := slice[i-1] + slice[i-2]
        slice = append(slice, next)
    }

    return slice

}

func main() {

}