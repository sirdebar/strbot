package main

import (
	"fmt"
)

func main() {
	slice := []int{1,2,3}
	copySlice := make([]int, 3)
	copy(copySlice, slice)
	fmt.Println(copySlice, slice)

	slice = append(slice, 4)
	fmt.Println(copySlice, slice)
}
