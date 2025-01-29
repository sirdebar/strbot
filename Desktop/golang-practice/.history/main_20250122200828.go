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
    library := Library{
        Books: []Book{
            {
                Title:       "Lorem ipsum",
                InStock:     true,
                PublishYear: 1984,
                Author:      Author{Name: "Jack"},
            },
            {
                Title:       "Another book",
                InStock:     true,
                PublishYear: 1990,
                Author:      Author{Name: "Jack"},
            },
            {
                Title:       "Different author",
                InStock:     false,
                PublishYear: 2000,
                Author:      Author{Name: "John"},
            },
        },
    }


}