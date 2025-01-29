package main

import (
    "fmt"
    "strings" // добавим для удобства поиска без учета регистра
)

// Author представляет автора книги
type Author struct {
    Name string
}

// Book представляет книгу
type Book struct {
    Title       string
    InStock     bool
    PublishYear int
    Author      // встраивание структуры Author
}

// Library представляет нашу библиотеку с коллекцией книг
type Library struct {
    Books []Book // слайс для хранения множества книг
}

// FindBooksByAuthor ищет все книги указанного автора
func (l *Library) FindBooksByAuthor(authorName string) []Book {
    // Создаем слайс для хранения найденных книг
    var foundBooks []Book
    
    // Приводим имя автора к нижнему регистру для поиска без учета регистра
    searchName := strings.ToLower(authorName)
    
    // Перебираем все книги в библиотеке
    for _, book := range l.Books {
        // Если имя автора совпадает, добавляем книгу в результат
        if strings.ToLower(book.Name) == searchName {
            foundBooks = append(foundBooks, book)
        }
    }
    
    return foundBooks
}

func main() {
    // Создаем библиотеку
    library := Library{
        Books: []Book{
            {
                Title:       "Lorem ipsum",
                InStock:     true,
                PublishYear: 1984,
                Author:      Author{Name: "Jack"},
            },
            {
                Title:       "Another book",
                InStock:     true,
                PublishYear: 1990,
                Author:      Author{Name: "Jack"},
            },
            {
                Title:       "Different author",
                InStock:     false,
                PublishYear: 2000,
                Author:      Author{Name: "John"},
            },
        },
    }

    fmt.Println("Hello, what you want to know?")
    var method string
    fmt.Scan(&method)

    if method == "Search author" {
        fmt.Println("Who do you want to search?")
        var authorName string
        fmt.Scan(&authorName)

        foundBooks := library.FindBooksByAuthor(authorName)
        
        if len(foundBooks) > 0 {
            fmt.Printf("Found %d books by %s:\n", len(foundBooks), authorName)
            for _, book := range foundBooks {
                fmt.Printf("- %s (%d)\n", book.Title, book.PublishYear)
            }
        } else {
            fmt.Printf("No books found by author: %s\n", authorName)
        }
    }
}