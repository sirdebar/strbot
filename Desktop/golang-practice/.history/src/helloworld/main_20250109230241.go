package main

import (
	"fmt"
)

func main() {
	slice := []int{1,2,3}
	copySlice := make([]int, [])
	copy(copySlice, slice)
	fmt.Println(copySlice)

	slice
	fmt.Println(slice)
}
