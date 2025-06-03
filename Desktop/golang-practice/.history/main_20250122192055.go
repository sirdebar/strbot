package main

import (
    "encoding/json"
    "fmt"
)

type Author struct {
    Name string
}

type Book struct {
    Title string
    Author
    InStock bool
}


func main() {

}