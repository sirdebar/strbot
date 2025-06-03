package main

import (
    "fmt"
)

type Author struct {
    Name string
}

type Book struct {
    Title string
    InStock bool
    PublishYear int
    Author
}

type Library struct {
    Book 
}


func main() {
    books := Book{"Lorem ipsum", true, 1984, Author{
        Name: "Jack",
    }, 
}
    fmt.Println("Hello, what you want to know?")
    var method string
    fmt.Scan(&method)
        if method == "Search author" {
            fmt.Println("Who do you want to search?")
            var authorName string
            fmt.Scan(&authorName)
                if authorName == books.Name {
                    fmt.Printf("Authors which were founded: %v", books.Author.Name)
                }
        }
    
}
