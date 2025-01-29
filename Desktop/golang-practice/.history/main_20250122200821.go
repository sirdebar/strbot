package main

import (
    "fmt"
    "strings" // добавим для удобства поиска без учета регистра
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

    fmt.Println("Hello, what you want to know?")
    var method string
    fmt.Scan(&method)

    if method == "Search author" {
        fmt.Println("Who do you want to search?")
        var authorName string
        fmt.Scan(&authorName)

        foundBooks := library.FindBooksByAuthor(authorName)
        
        if len(foundBooks) > 0 {
            fmt.Printf("Found %d books by %s:\n", len(foundBooks), authorName)
            for _, book := range foundBooks {
                fmt.Printf("- %s (%d)\n", book.Title, book.PublishYear)
            }
        } else {
            fmt.Printf("No books found by author: %s\n", authorName)
        }
    }
}