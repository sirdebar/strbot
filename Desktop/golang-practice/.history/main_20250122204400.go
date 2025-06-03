package main

import (
    "fmt"
    "strings"
)

type Book struct {
    Title   string
    InStock bool
}

type Library struct {
    Books []Book
}

// Метод для аренды книги
func (l *Library) rentBook(bookTitle string) error {
    // Ищем книгу по названию, игнорируя регистр для удобства пользователя
    for i := range l.Books {
        if strings.EqualFold(l.Books[i].Title, bookTitle) {
            // Проверяем, доступна ли книга
            if !l.Books[i].InStock {
                return fmt.Errorf("книга '%s' уже арендована", bookTitle)
            }
            // Отмечаем книгу как взятую
            l.Books[i].InStock = false
            return nil
        }
    }
    return fmt.Errorf("книга '%s' не найдена", bookTitle)
}

// Метод для возврата книги
func (l *Library) returnBook(bookTitle string) error {
    for i := range l.Books {
        if strings.EqualFold(l.Books[i].Title, bookTitle) {
            // Проверяем, была ли книга арендована
            if l.Books[i].InStock {
                return fmt.Errorf("книга '%s' не была арендована", bookTitle)
            }
            // Отмечаем книгу как возвращенную
            l.Books[i].InStock = true
            return nil
        }
    }
    return fmt.Errorf("книга '%s' не найдена", bookTitle)
}

// Метод для отображения всех книг с их статусом
func (l *Library) displayBooks() {
    fmt.Println("\nСписок всех книг:")
    for _, book := range l.Books {
        status := "доступна"
        if !book.InStock {
            status = "арендована"
        }
        fmt.Printf("- %s (%s)\n", book.Title, status)
    }
}

func main() {
    // Создаем библиотеку с начальными книгами
    library := Library{
        Books: []Book{
            {Title: "Lorem", InStock: true},
            {Title: "Ipsum", InStock: true},
        },
    }

    // Бесконечный цикл для работы с библиотекой
    for {
        fmt.Println("\nВыберите действие:")
        fmt.Println("1. Посмотреть все книги")
        fmt.Println("2. Арендовать книгу")
        fmt.Println("3. Вернуть книгу")
        fmt.Println("4. Выйти")

        var choice string
        fmt.Scan(&choice)

        switch choice {
        case "1":
            library.displayBooks()

        case "2":
            fmt.Println("Какую книгу хотите арендовать?")
            var bookTitle string
            fmt.Scanf("%s\n", &bookTitle) // Используем Scanf для чтения строки целиком
            
            err := library.rentBook(bookTitle)
            if err != nil {
                fmt.Println("Ошибка:", err)
            } else {
                fmt.Printf("Книга '%s' успешно арендована\n", bookTitle)
            }

        case "3":
            fmt.Println("Какую книгу хотите вернуть?")
            var bookTitle string
            fmt.Scanf("%s\n", &bookTitle)
            
            err := library.returnBook(bookTitle)
            if err != nil {
                fmt.Println("Ошибка:", err)
            } else {
                fmt.Printf("Книга '%s' успешно возвращена\n", bookTitle)
            }

        case "4":
            fmt.Println("До свидания!")
            return

        default:
            fmt.Println("Неизвестная команда")
        }
    }
}