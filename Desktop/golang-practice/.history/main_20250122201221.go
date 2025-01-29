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

func

func main() {
    library := Library{
        Books: []Book{
            {
                Title: "Lorem", InStock: true,
            },
            {
                Title: "Ipsum", InStock: false,
            },
        },
    }
    fmt.Println("Which book you want to rent?")
    var data string
    fmt.Scan(&data)

}