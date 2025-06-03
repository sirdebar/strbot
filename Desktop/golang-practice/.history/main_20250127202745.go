package main

import (
	"fmt"
)

func main() {
m := [3]int{1,2,3}
res1 := &m
slice := []int{1,2,3}
slice = append(slice, 4)
res2 := &slice
fmt.Println(res1,res2)
}


