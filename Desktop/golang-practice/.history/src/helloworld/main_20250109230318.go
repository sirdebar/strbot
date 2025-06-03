package main

import (
	"fmt"
)

func main() {
	slice := []int{1,2,3}
	copySlice := make([]int, 2)
	copy(copySlice, slice)
	fmt.Println(copySlice)

	slice = append(slice, )
	fmt.Println(slice)
}
