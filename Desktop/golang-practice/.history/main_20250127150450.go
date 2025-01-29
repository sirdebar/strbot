package main

import (
    "fmt"
)

func main() {
    numbers := map[string]int{
        "M": 1000,
        "D": 500,
        "C": 100,
        "L": 50,
        "X": 10,
        "V": 5,
        "I": 1,
    }

    fmt.Println("Enter number to convert into rome:")
    var input int
    fmt.Scan(&input)

    res := convert(input)
    fmt.Print("There are converted number:", res)
}