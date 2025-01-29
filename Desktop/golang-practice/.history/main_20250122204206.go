package main

import (
    "fmt"
)

type Book struct {
    Title string
    InStock bool
}

type Library struct {
    Books []Book
}

func (l *Library) rentBook(bookTitle string){
    if bookTitle ==  {

    }
}

func main() {
    library := Library{
        Books: []Book{
            {
                Title: "Lorem", InStock: true,
            },
            {
                Title: "Ipsum", InStock: true,
            },
        },
    }
    fmt.Printf("Books that we have: %v\n", library.Books)
    fmt.Println("Which book you want to rent?")
    var bookTitle string
    fmt.Scan(&bookTitle)


    

}