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
    Author
    InStock bool
    PublishYear int
}


func main() {
    fmt.Println("Hello, what you want to know?")
    var method string
    fmt.Scan(&method)
    if err != nil {
        
    }
    
}

func takeBook() {

}