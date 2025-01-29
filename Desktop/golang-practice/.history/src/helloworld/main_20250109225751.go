package main

import (
	"fmt"
)

func main() {
	arr := [5]int{1,2,3,4,5}
	slice := arr[4:]
	// newSlice := append(slice, 6)
	arr[4] = 11
	fmt.Println(slice)
}
