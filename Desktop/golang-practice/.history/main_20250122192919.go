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
    books := Book{"Lorem ipsum", Author{
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

    }
    
}

func takeBook() {

}