package main

import (
	"fmt"
)

func main() {

type person struct {
	Name string
	Age int
}

type workers struct {
	Info person
	Job string
}

w := workers{
	Info: person{
		Name: "John",
		Age: 29
	},
	Job: "Director",
}

fmt.Print(w)

}




