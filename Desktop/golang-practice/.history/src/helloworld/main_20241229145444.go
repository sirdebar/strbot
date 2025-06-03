package main

import (
	"fmt"
)

type Info struct {
	Password  string
	PublicKey int
	SecretKey int
}

func main() {
	// Определяем структуру Info


	// Создаем карту пользователей
	users := make(map[string]Info)
	users["Bobby"] = Info{Password: "Qwerty123", PublicKey: 123, SecretKey: 8812346381}

	// Авторизация
	authorize(users)
}

func authorize(users map[string]Info) {
	var name string
	var pw string

	fmt.Println("Hello! To authorize, enter your name:")
	fmt.Scan(&name)

	// Проверяем, существует ли пользователь
	userInfo, exists := users[name]
	if !exists {
		panic("User not found!")
	}

	// Проверяем пароль
	fmt.Println("Great, now enter your password:")
	fmt.Scan(&pw)

	if pw == userInfo.Password {
		fmt.Printf("You're authorized now! Here are your API keys: %d (Public), %d (Secret)\n", userInfo.PublicKey, userInfo.SecretKey)
	} else {
		panic("Invalid password!")
	}
}

func safeAuthorize(users map[string]Info) (success bool) {
	defer func() {
		if r := recover(); r != nil {
			fmt.Printf("Error:%v", r)
		}
	}
}