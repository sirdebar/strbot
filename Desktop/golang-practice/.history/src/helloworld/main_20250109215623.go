package main

import (
	"fmt"
)

func main() {
	slice := []int{1,2,3,4,5,6,7,8,9,10}
	var index int
	fmt.Println("Enter index to remove:")
	fmt.Scanln(index)

	slice = append(slice[:index], slice[] )
}
