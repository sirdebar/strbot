// package main

// import (
//     "fmt"
//     "sort"
//     "os"
//     "bufio"
//     "strconv"
// )

// func main() {
//     numbers := []int{}

//     fmt.Println("Enter couple of integers:")
//     sc := bufio.NewScanner(os.Stdin)

//     for sc.Scan() {
//         fmt.Print(">")
//         txt := sc.Text()
//         if txt == "done" {
//             break
//         }

//         intTxt, err := strconv.Atoi(txt)
//         if err != nil {
//             fmt.Println("Invalid input. Please try integer or type 'done' to finish.")
//             continue
//         }

//         numbers = append(numbers, intTxt)
//     }
//     sorting(numbers)
//     fmt.Println("In increasing order:", numbers)
//     }


// func sorting(n []int) {
//     sort.Ints(n)
// }


