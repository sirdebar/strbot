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



}

func counter(w string) map[rune]int {
	for i := len(w) - 1; i >= 0; i-- {
		char := rune(w[i])

	}
}


