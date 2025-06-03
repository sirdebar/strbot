package main

import (
	"fmt"
)

func main() {

type employee struct {
	Name string
	Id int
}
fmt.Println(e)
e := employee{"John", 1}

copyStruct := &e
copyStruct.Name = "Jane"
fmt.Println (copyStruct)

}




