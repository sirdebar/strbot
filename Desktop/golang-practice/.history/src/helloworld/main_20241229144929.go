package main

import (
	"fmt"
)

func main() {
	type Info struct {
		Password string
		PublicKey int
		SecretKey int
	}

	users := make(map[string]Info)

	users["Bobby"] = Info{Password: "Qwerty123", PublicKey: 123, SecretKey: 8812346381}

	authorize(users)
}

func authorize(users map[string]Info) {
	var name string
	var pw string

	fmt.Println("Hello! To authorize enter name:")
	fmt.Scan(&name)

	userInfo, exists := users[name]
	if !exists {
		panic("User not found!")
	}

	fmt.Println("Great, now enter your password:")
	fmt.Scan(&pw)

	if pw == userInfo.Password {
		fmt.Printf("You're authorized now! Here are your API keys: %d (Public), %d (Secret)\n", userInfo.PublicKey, userInfo.SecretKey)
	} else {
		panic("Invalid password!")
	}

}


