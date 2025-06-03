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




//package main

// import (
// 	"fmt"
// )

// type Info struct {
// 	Password  string
// 	PublicKey int
// 	SecretKey int
// }

// func main() {
// 	users := make(map[string]Info)
// 	users["Bobby"] = Info{Password: "Qwerty123", PublicKey: 123, SecretKey: 8812346381}

// 	for {
// 		if success := safeAuthorize(users); success {
// 			fmt.Println("Authorization completed successfully!")
// 			break
// 	} else {
// 		fmt.Println("Authorization failed, please try again.")
// 	}

// 	fmt.Println("Want to retry?(yes/no)")
// 	var response string
// 	fmt.Scan(&response)
// 	if response == "no" || response == "exit" {
// 		fmt.Println("Bye!")
// 		break
// 	}
// }
// }

// func authorize(users map[string]Info) {
// 	var name string
// 	var pw string

// 	fmt.Println("Hello! To authorize, enter your name:")
// 	fmt.Scan(&name)

// 	userInfo, exists := users[name]
// 	if !exists {
// 		panic("User not found!")
// 	}

// 	fmt.Println("Great, now enter your password:")
// 	fmt.Scan(&pw)

// 	if pw == "exit" {
// 		panic("Exiting")
// 	}
	
// 	if pw == userInfo.Password {
// 		fmt.Printf("You're authorized now!\n Here are your API keys: %d (Public), %d (Secret)\n", userInfo.PublicKey, userInfo.SecretKey)
// 	} else {
// 		panic("Invalid password!")
// 	}
// }

// func safeAuthorize(users map[string]Info) (success bool) {
// 	defer func() {
// 		if r := recover(); r != nil {
// 			fmt.Printf("Error:%v", r)
// 			success = false
// 		}
// 	}()

// 		authorize(users)
// 		return true
// 	}