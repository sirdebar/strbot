package main

import (
	"fmt"
	"strings"
)



func main() {
	fmt.Print("Input: ")
	var word string

	fmt.Scan(&word)
	res := counter(word)
	fmt.Print(res)
}



