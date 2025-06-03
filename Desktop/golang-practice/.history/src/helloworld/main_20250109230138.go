package main

import (
	"fmt"
)

func main() {
	slice := []int{1,2,3}
	copySlice := make([]int, slice)
	copy(copySlice, len)
	fmt.Println(copySlice)

	slice
	fmt.Println(slice)
}
