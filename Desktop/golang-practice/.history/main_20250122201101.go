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
    library := Library{
        Books: []Book{
            {
                Title: "Lorem",
            }
        },
    }
    fmt.Println("Which book you want to rent?")

}