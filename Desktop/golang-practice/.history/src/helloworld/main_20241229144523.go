package main

import (
	"bufio"
	"fmt"
	"os"
)

func main() {
	type Info struct {
		Password string
		PublicKey int
		SecretKey int
	}

	users := make(map[string]Info)

	users["Bobby"] = Info{Password: "Qwerty123", PublicKey: 123, SecretKey: 8812346381}



	fmt.Println()
}

func authorize(u users, i Info) {
	var name string
	var pw string
	fmt.Println("Hello! To authorize enter name:")
	fmt.Scan(&name)
	value, exists := i[name]
	if exists {
		fmt.Println("Great, now enter your password:")
		fmt.Scan(&pw)
			if pw == i.Password {
				fmt.Printf("You're authorized now! Here are your API keys: %d, %d\n", PublicKey, SecretKey)
			} else {
				panic("Invalid password")
			}
	} else {
		panic("")
	}
}

