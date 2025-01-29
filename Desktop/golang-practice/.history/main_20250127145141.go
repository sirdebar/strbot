package main

import (
    "fmt"
)

func main() {
    fmt.Println("Введите число, чтобы увидеть для него ряд фибоначчи")
    var slice []int

    var num int
    fmt.Scan(&num)

    for i := 0; i < num; i++ {
        a := 0
        b := a + 1
        for x := 0; x == num; a++ {
            slice = append(slice, a+b)
        }
    }
    fmt.Println(slice)
}