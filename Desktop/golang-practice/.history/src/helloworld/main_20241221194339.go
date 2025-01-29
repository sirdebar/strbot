package main

import (
    "fmt"
    "math/rand"
    "time"
)

func main() {
    var num int32
    sec := time.Now().Unix()
    rand.Seed(sec)

    for {
        fmt.Print("Writing inside the loop...")
        if num = rand.Int31n(10); num == 5 {
            fmt.Println("finish!")
            break
        }
        fmt.Println(num)
    }
}