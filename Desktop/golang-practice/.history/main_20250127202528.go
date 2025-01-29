package main

import (
	"fmt"
	"strings"
)

func main() {
	fmt.Println("Enter number to convert into rome:")
	var input string
	fmt.Scan(&input)

	res := convert(input)
	fmt.Print("There are converted number:", res)
}


