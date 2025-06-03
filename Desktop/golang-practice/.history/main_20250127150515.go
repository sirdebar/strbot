package main

import (
    "fmt"
)

func main() {
    fmt.Println("Enter number to convert into rome:")
    var input int
    fmt.Scan(&input)

    res := convert(input)
    fmt.Print("There are converted number:", res)
}

func convert() {

}