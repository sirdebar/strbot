import { type Topic, type Lesson, type Post, type InsertTopic, type InsertLesson, type InsertPost, topicsTable, lessonsTable, postsTable, pageViewsTable } from "@shared/schema";
import { randomUUID } from "crypto";
import { drizzle } from "drizzle-orm/neon-http";
import { eq, desc, count } from "drizzle-orm";
import { sql } from "drizzle-orm";

export interface IStorage {
  // Topics
  getTopics(): Promise<Topic[]>;
  getTopic(id: string): Promise<Topic | undefined>;
  createTopic(topic: InsertTopic): Promise<Topic>;
  updateTopic(id: string, topic: InsertTopic): Promise<Topic | undefined>;
  deleteTopic(id: string): Promise<boolean>;

  // Lessons
  getLessons(): Promise<Lesson[]>;
  getLesson(id: string): Promise<Lesson | undefined>;
  getLessonsByTopic(topicId: string): Promise<Lesson[]>;
  createLesson(lesson: InsertLesson): Promise<Lesson>;
  updateLesson(id: string, lesson: InsertLesson): Promise<Lesson | undefined>;
  deleteLesson(id: string): Promise<boolean>;

  // Posts (Blog)
  getPosts(): Promise<Post[]>;
  getPost(id: string): Promise<Post | undefined>;
  createPost(post: InsertPost): Promise<Post>;
  updatePost(id: string, post: InsertPost): Promise<Post | undefined>;
  deletePost(id: string): Promise<boolean>;

  // Page Views
  recordPageView(path: string, ip: string): Promise<void>;
  getPageViewStats(): Promise<{ uniqueVisits: number; totalVisits: number }>;
}

class DBStorage implements IStorage {
  private db: ReturnType<typeof drizzle>;

  constructor() {
    const databaseUrl = process.env.DATABASE_URL;
    if (!databaseUrl) {
      throw new Error("DATABASE_URL is not set");
    }
    this.db = drizzle(databaseUrl);
    this.initializeSampleData();
  }

  private async initializeSampleData() {
    try {
      const existingTopics = await this.db.select().from(topicsTable).limit(1);
      if (existingTopics.length > 0) {
        return; // Data already exists
      }

      const sampleTopics = [
        {
          id: "intro",
          titleRu: "Введение в Go",
          titleEn: "Introduction to Go",
          descriptionRu: "Первые шаги в мире Go: установка, настройка среды и первая программа",
          descriptionEn: "First steps in Go world: installation, environment setup, and first program",
          order: 1,
          icon: "book",
        },
        {
          id: "types",
          titleRu: "Типы данных",
          titleEn: "Data Types",
          descriptionRu: "Изучаем примитивные типы, массивы, слайсы и структуры",
          descriptionEn: "Learning primitive types, arrays, slices, and structs",
          order: 2,
          icon: "layers",
        },
        {
          id: "functions",
          titleRu: "Функции",
          titleEn: "Functions",
          descriptionRu: "Объявление функций, множественные возвращаемые значения и замыкания",
          descriptionEn: "Function declarations, multiple return values, and closures",
          order: 3,
          icon: "code",
        },
        {
          id: "oop",
          titleRu: "ООП в Go",
          titleEn: "OOP in Go",
          descriptionRu: "Интерфейсы, методы и композиция вместо наследования",
          descriptionEn: "Interfaces, methods, and composition over inheritance",
          order: 4,
          icon: "git",
        },
        {
          id: "concurrency",
          titleRu: "Конкурентность",
          titleEn: "Concurrency",
          descriptionRu: "Горутины, каналы и паттерны параллельного программирования",
          descriptionEn: "Goroutines, channels, and parallel programming patterns",
          order: 5,
          icon: "zap",
        },
        {
          id: "concurrency2",
          titleRu: "Конкурентность Ч.2",
          titleEn: "Concurrency Part 2",
          descriptionRu: "Продвинутые паттерны: мьютексы, waitgroups и контекст",
          descriptionEn: "Advanced patterns: mutexes, waitgroups, and context",
          order: 6,
          icon: "database",
        },
      ];

      const sampleLessons = [
        {
          id: "intro-1",
          topicId: "intro",
          titleRu: "Что такое Go?",
          titleEn: "What is Go?",
          contentRu: `<h2>Добро пожаловать в мир Go!</h2>
<p>Go (или Golang) — это современный язык программирования, созданный в Google в 2009 году. Он разработан Робертом Грисемером, Робом Пайком и Кеном Томпсоном — легендами мира программирования.</p>
<h3>Почему Go?</h3>
<p>Go сочетает в себе:</p>
<ul>
<li><strong>Простоту</strong> — минималистичный синтаксис, который легко читать</li>
<li><strong>Скорость</strong> — компилируется в машинный код</li>
<li><strong>Конкурентность</strong> — встроенная поддержка параллельного программирования</li>
</ul>
<p>В следующем уроке мы установим Go и напишем нашу первую программу.</p>`,
          contentEn: `<h2>Welcome to the World of Go!</h2>
<p>Go (or Golang) is a modern programming language created at Google in 2009. It was designed by Robert Griesemer, Rob Pike, and Ken Thompson — legends of the programming world.</p>
<h3>Why Go?</h3>
<p>Go combines:</p>
<ul>
<li><strong>Simplicity</strong> — minimalist syntax that's easy to read</li>
<li><strong>Speed</strong> — compiles to machine code</li>
<li><strong>Concurrency</strong> — built-in support for parallel programming</li>
</ul>
<p>In the next lesson, we'll install Go and write our first program.</p>`,
          order: 1,
        },
        {
          id: "intro-2",
          topicId: "intro",
          titleRu: "Установка Go",
          titleEn: "Installing Go",
          contentRu: `<h2>Установка Go</h2>
<p>Скачайте Go с официального сайта <a href="https://go.dev/dl/">go.dev/dl</a> и следуйте инструкциям для вашей операционной системы.</p>
<h3>Проверка установки</h3>
<p>После установки откройте терминал и выполните:</p>
<pre><code>go version</code></pre>
<p>Вы должны увидеть версию Go, например: <code>go version go1.21.0 darwin/amd64</code></p>`,
          contentEn: `<h2>Installing Go</h2>
<p>Download Go from the official website <a href="https://go.dev/dl/">go.dev/dl</a> and follow the instructions for your operating system.</p>
<h3>Verify Installation</h3>
<p>After installation, open terminal and run:</p>
<pre><code>go version</code></pre>
<p>You should see the Go version, for example: <code>go version go1.21.0 darwin/amd64</code></p>`,
          order: 2,
        },
        {
          id: "intro-3",
          topicId: "intro",
          titleRu: "Hello, World!",
          titleEn: "Hello, World!",
          contentRu: `<h2>Первая программа на Go</h2>
<p>Создайте файл <code>main.go</code>:</p>
<pre><code>package main

import "fmt"

func main() {
    fmt.Println("Привет, Мир!")
}</code></pre>
<p>Запустите программу:</p>
<pre><code>go run main.go</code></pre>
<p>Поздравляем! Вы написали свою первую программу на Go. 🎉</p>`,
          contentEn: `<h2>First Go Program</h2>
<p>Create a file <code>main.go</code>:</p>
<pre><code>package main

import "fmt"

func main() {
    fmt.Println("Hello, World!")
}</code></pre>
<p>Run the program:</p>
<pre><code>go run main.go</code></pre>
<p>Congratulations! You've written your first Go program.</p>`,
          order: 3,
        },
        {
          id: "types-1",
          topicId: "types",
          titleRu: "Примитивные типы",
          titleEn: "Primitive Types",
          contentRu: `<h2>Базовые типы данных в Go</h2>
<p>Go — строго типизированный язык. Вот основные типы:</p>
<h3>Целые числа</h3>
<pre><code>var age int = 25
var count int64 = 1000000000</code></pre>
<h3>Числа с плавающей точкой</h3>
<pre><code>var pi float64 = 3.14159
var temp float32 = -40.5</code></pre>
<h3>Строки и булевы значения</h3>
<pre><code>var name string = "Gopher"
var isActive bool = true</code></pre>`,
          contentEn: `<h2>Basic Data Types in Go</h2>
<p>Go is a strongly typed language. Here are the basic types:</p>
<h3>Integers</h3>
<pre><code>var age int = 25
var count int64 = 1000000000</code></pre>
<h3>Floating Point Numbers</h3>
<pre><code>var pi float64 = 3.14159
var temp float32 = -40.5</code></pre>
<h3>Strings and Booleans</h3>
<pre><code>var name string = "Gopher"
var isActive bool = true</code></pre>`,
          order: 1,
        },
        {
          id: "concurrency-1",
          topicId: "concurrency",
          titleRu: "Горутины",
          titleEn: "Goroutines",
          contentRu: `<h2>Горутины — сердце конкурентности Go</h2>
<p>Горутина — это легковесный поток, управляемый Go runtime. Запуск горутины невероятно прост:</p>
<pre><code>go func() {
    fmt.Println("Я выполняюсь параллельно!")
}()</code></pre>
<p>Горутины потребляют всего около <strong>2KB</strong> памяти при старте (против мегабайтов для обычных потоков).</p>`,
          contentEn: `<h2>Goroutines — The Heart of Go Concurrency</h2>
<p>A goroutine is a lightweight thread managed by Go runtime. Starting a goroutine is incredibly simple:</p>
<pre><code>go func() {
    fmt.Println("I'm running in parallel!")
}()</code></pre>
<p>Goroutines consume only about <strong>2KB</strong> of memory at start (compared to megabytes for regular threads).</p>`,
          order: 1,
        },
        {
          id: "concurrency2-1",
          topicId: "concurrency2",
          titleRu: "Мьютексы",
          titleEn: "Mutexes",
          contentRu: `<h2>Мьютексы для безопасного доступа к данным</h2>
<p>Когда несколько горутин обращаются к общим данным, нужна синхронизация:</p>
<pre><code>import "sync"

var mu sync.Mutex
var counter int

func increment() {
    mu.Lock()
    counter++
    mu.Unlock()
}</code></pre>
<p><strong>Важно:</strong> Всегда освобождайте мьютекс с помощью <code>defer mu.Unlock()</code> для избежания дедлоков.</p>`,
          contentEn: `<h2>Mutexes for Safe Data Access</h2>
<p>When multiple goroutines access shared data, synchronization is needed:</p>
<pre><code>import "sync"

var mu sync.Mutex
var counter int

func increment() {
    mu.Lock()
    counter++
    mu.Unlock()
}</code></pre>
<p><strong>Important:</strong> Always release mutex with <code>defer mu.Unlock()</code> to avoid deadlocks.</p>`,
          order: 1,
        },
      ];

      await this.db.insert(topicsTable).values(sampleTopics);
      await this.db.insert(lessonsTable).values(sampleLessons);
      console.log("Sample data initialized");
    } catch (error) {
      console.log("Sample data already exists or initialization skipped:", error);
    }
  }

  // Topics
  async getTopics(): Promise<Topic[]> {
    return this.db.select().from(topicsTable);
  }

  async getTopic(id: string): Promise<Topic | undefined> {
    const result = await this.db.select().from(topicsTable).where(eq(topicsTable.id, id));
    return result[0];
  }

  async createTopic(insertTopic: InsertTopic): Promise<Topic> {
    const id = randomUUID();
    const topic: Topic = { id, ...insertTopic } as Topic;
    await this.db.insert(topicsTable).values(topic);
    return topic;
  }

  async updateTopic(id: string, insertTopic: InsertTopic): Promise<Topic | undefined> {
    const topic: Topic = { id, ...insertTopic } as Topic;
    const result = await this.db.update(topicsTable).set(topic).where(eq(topicsTable.id, id)).returning();
    return result[0];
  }

  async deleteTopic(id: string): Promise<boolean> {
    await this.db.delete(lessonsTable).where(eq(lessonsTable.topicId, id));
    const result = await this.db.delete(topicsTable).where(eq(topicsTable.id, id));
    return result.rowCount > 0;
  }

  // Lessons
  async getLessons(): Promise<Lesson[]> {
    return this.db.select().from(lessonsTable);
  }

  async getLesson(id: string): Promise<Lesson | undefined> {
    const result = await this.db.select().from(lessonsTable).where(eq(lessonsTable.id, id));
    return result[0];
  }

  async getLessonsByTopic(topicId: string): Promise<Lesson[]> {
    return this.db.select().from(lessonsTable).where(eq(lessonsTable.topicId, topicId));
  }

  async createLesson(insertLesson: InsertLesson): Promise<Lesson> {
    const id = randomUUID();
    const lesson: Lesson = { id, ...insertLesson } as Lesson;
    await this.db.insert(lessonsTable).values(lesson);
    return lesson;
  }

  async updateLesson(id: string, insertLesson: InsertLesson): Promise<Lesson | undefined> {
    const lesson: Lesson = { id, ...insertLesson } as Lesson;
    const result = await this.db.update(lessonsTable).set(lesson).where(eq(lessonsTable.id, id)).returning();
    return result[0];
  }

  async deleteLesson(id: string): Promise<boolean> {
    const result = await this.db.delete(lessonsTable).where(eq(lessonsTable.id, id));
    return result.rowCount > 0;
  }

  // Posts (Blog)
  async getPosts(): Promise<Post[]> {
    return this.db.select().from(postsTable).orderBy(desc(postsTable.createdAt));
  }

  async getPost(id: string): Promise<Post | undefined> {
    const result = await this.db.select().from(postsTable).where(eq(postsTable.id, id));
    return result[0];
  }

  async createPost(insertPost: InsertPost): Promise<Post> {
    const id = randomUUID();
    const post: Post = { 
      id, 
      ...insertPost,
      createdAt: new Date()
    } as Post;
    await this.db.insert(postsTable).values(post);
    return post;
  }

  async updatePost(id: string, insertPost: InsertPost): Promise<Post | undefined> {
    const post: Partial<Post> = { ...insertPost };
    const result = await this.db.update(postsTable).set(post).where(eq(postsTable.id, id)).returning();
    return result[0];
  }

  async deletePost(id: string): Promise<boolean> {
    const result = await this.db.delete(postsTable).where(eq(postsTable.id, id));
    return result.rowCount > 0;
  }

  async recordPageView(path: string, ip: string): Promise<void> {
    await this.db.insert(pageViewsTable).values({ path, ip });
  }

  async getPageViewStats(): Promise<{ uniqueVisits: number; totalVisits: number }> {
    const views = await this.db.select().from(pageViewsTable).where(eq(pageViewsTable.path, "/"));
    const uniqueIPs = new Set(views.map(v => v.ip)).size;
    return {
      uniqueVisits: uniqueIPs,
      totalVisits: views.length,
    };
  }
}

export const storage = new DBStorage();
