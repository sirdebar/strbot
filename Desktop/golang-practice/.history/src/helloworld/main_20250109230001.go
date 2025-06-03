package main

import (
	"fmt"
)

func main() {
	slice := []int{1,2,3}
	copySlice := make(slice)
	fmt.Println(slice)
}
