package main

import (
    "fmt"
)

type Book struct {
    Title       string
    InStock     bool
}

type Library struct {
    Books []Book
}

func main() {
    lib
    fmt.Println("Which book you want to rent?")

}