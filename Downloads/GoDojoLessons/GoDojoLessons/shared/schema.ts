import { pgTable, serial, text, varchar, integer, timestamp } from "drizzle-orm/pg-core";
import { z } from "zod";
import { createInsertSchema, createSelectSchema } from "drizzle-zod";

// Drizzle Tables
export const topicsTable = pgTable("topics", {
  id: varchar("id").primaryKey(),
  titleRu: text("title_ru").notNull(),
  titleEn: text("title_en").notNull(),
  descriptionRu: text("description_ru").notNull(),
  descriptionEn: text("description_en").notNull(),
  order: integer("order").notNull(),
  icon: varchar("icon"),
});

export const lessonsTable = pgTable("lessons", {
  id: varchar("id").primaryKey(),
  topicId: varchar("topic_id").notNull(),
  titleRu: text("title_ru").notNull(),
  titleEn: text("title_en").notNull(),
  contentRu: text("content_ru").notNull(),
  contentEn: text("content_en").notNull(),
  order: integer("order").notNull(),
});

export const postsTable = pgTable("posts", {
  id: varchar("id").primaryKey(),
  titleRu: text("title_ru").notNull(),
  titleEn: text("title_en").notNull(),
  contentRu: text("content_ru").notNull(),
  contentEn: text("content_en").notNull(),
  createdAt: timestamp("created_at").notNull().defaultNow(),
  order: integer("order").notNull(),
});

export const pageViewsTable = pgTable("page_views", {
  id: serial("id").primaryKey(),
  path: varchar("path").notNull(),
  ip: varchar("ip").notNull(),
  timestamp: timestamp("timestamp").notNull().defaultNow(),
});

// Zod Schemas
export const topicSchema = createSelectSchema(topicsTable);
export const lessonSchema = createSelectSchema(lessonsTable);
export const postSchema = createSelectSchema(postsTable);
export const pageViewSchema = createSelectSchema(pageViewsTable);

export const insertTopicSchema = createInsertSchema(topicsTable).omit({ id: true });
export const insertLessonSchema = createInsertSchema(lessonsTable).omit({ id: true });
export const insertPostSchema = createInsertSchema(postsTable).omit({ id: true, createdAt: true });

// Types
export type Topic = z.infer<typeof topicSchema>;
export type Lesson = z.infer<typeof lessonSchema>;
export type Post = z.infer<typeof postSchema>;
export type PageView = z.infer<typeof pageViewSchema>;
export type InsertTopic = z.infer<typeof insertTopicSchema>;
export type InsertLesson = z.infer<typeof insertLessonSchema>;
export type InsertPost = z.infer<typeof insertPostSchema>;

export const users = {
  id: "",
  username: "",
  password: "",
};

export type User = typeof users;
export type InsertUser = Omit<User, "id">;
