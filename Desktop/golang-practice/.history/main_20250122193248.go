package main

import (
    "encoding/json"
    "fmt"
)

type Author struct {
    Name string
    Surname string
}

type Book struct {
    Title string
    InStock bool
    PublishYear int
    Author
}


func main() {
    books := Book{"Lorem ipsum", true, 1984, Author{
        Name: "Jack", Surname: "Smith",
    }, 
}
    fmt.Println("Hello, what you want to know?")
    var method string
    fmt.Scan(&method)
        if method == "Search author" {
            fmt.Println("Who do you want to search?")
            var authorName string
            fmt.Scan(&authorName)
                if authorName == books.Name + "" + books.Surname {
                    fmt.Printf("Authors which were founded: %v", books.Author.Name + books.Author.Surname)
                }
        }
    
}

func takeBook() {

}