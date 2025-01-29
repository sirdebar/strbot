package main

import (
    "fmt"
)

type Author struct {
    Name string
}

type Book struct {
    Title       string
    InStock     bool
    PublishYear int
    Author
}

type Library struct {
    Books []Book
}


func main() {

    

}