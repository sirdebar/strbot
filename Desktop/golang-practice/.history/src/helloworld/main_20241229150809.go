package main

import (
	"fmt"
	"os"
	"io/ioutil"
)



func main() {

}

func authorize(users map[string]Info) {
	var name string
	var pw string

	fmt.Println("Hello! To authorize, enter your name:")
	fmt.Scan(&name)

	userInfo, exists := users[name]
	if !exists {
		panic("User not found!")
	}

	fmt.Println("Great, now enter your password:")
	fmt.Scan(&pw)

	if pw == "exit" {
		panic("Exiting")
	}
	
	if pw == userInfo.Password {
		fmt.Printf("You're authorized now!\n Here are your API keys: %d (Public), %d (Secret)\n", userInfo.PublicKey, userInfo.SecretKey)
	} else {
		panic("Invalid password!")
	}
}

func safeAuthorize(users map[string]Info) (success bool) {
	defer func() {
		if r := recover(); r != nil {
			fmt.Printf("Error:%v", r)
			success = false
		}
	}()

		authorize(users)
		return true
	}