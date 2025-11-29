import type { Express } from "express";
import { createServer, type Server } from "http";
import { storage } from "./storage";
import { insertTopicSchema, insertLessonSchema, insertPostSchema } from "@shared/schema";

const ADMIN_PASSWORD = "Semen10082008";

export async function registerRoutes(
  httpServer: Server,
  app: Express
): Promise<Server> {
  
  // Admin login
  app.post("/api/admin/login", async (req, res) => {
    const { password } = req.body;
    if (password === ADMIN_PASSWORD) {
      res.json({ success: true });
    } else {
      res.status(401).json({ error: "Invalid password" });
    }
  });

  // Topics
  app.get("/api/topics", async (_req, res) => {
    const topics = await storage.getTopics();
    res.json(topics);
  });

  app.get("/api/topics/:id", async (req, res) => {
    const topic = await storage.getTopic(req.params.id);
    if (!topic) {
      return res.status(404).json({ error: "Topic not found" });
    }
    res.json(topic);
  });

  app.get("/api/topics/:id/lessons", async (req, res) => {
    const lessons = await storage.getLessonsByTopic(req.params.id);
    res.json(lessons);
  });

  app.post("/api/topics", async (req, res) => {
    const result = insertTopicSchema.safeParse(req.body);
    if (!result.success) {
      return res.status(400).json({ error: result.error.message });
    }
    const topic = await storage.createTopic(result.data);
    res.status(201).json(topic);
  });

  app.put("/api/topics/:id", async (req, res) => {
    const result = insertTopicSchema.safeParse(req.body);
    if (!result.success) {
      return res.status(400).json({ error: result.error.message });
    }
    const topic = await storage.updateTopic(req.params.id, result.data);
    if (!topic) {
      return res.status(404).json({ error: "Topic not found" });
    }
    res.json(topic);
  });

  app.delete("/api/topics/:id", async (req, res) => {
    const deleted = await storage.deleteTopic(req.params.id);
    if (!deleted) {
      return res.status(404).json({ error: "Topic not found" });
    }
    res.json({ success: true });
  });

  // Lessons
  app.get("/api/lessons", async (_req, res) => {
    const lessons = await storage.getLessons();
    res.json(lessons);
  });

  app.get("/api/lessons/:id", async (req, res) => {
    const lesson = await storage.getLesson(req.params.id);
    if (!lesson) {
      return res.status(404).json({ error: "Lesson not found" });
    }
    res.json(lesson);
  });

  app.post("/api/lessons", async (req, res) => {
    const result = insertLessonSchema.safeParse(req.body);
    if (!result.success) {
      return res.status(400).json({ error: result.error.message });
    }
    const lesson = await storage.createLesson(result.data);
    res.status(201).json(lesson);
  });

  app.put("/api/lessons/:id", async (req, res) => {
    const result = insertLessonSchema.safeParse(req.body);
    if (!result.success) {
      return res.status(400).json({ error: result.error.message });
    }
    const lesson = await storage.updateLesson(req.params.id, result.data);
    if (!lesson) {
      return res.status(404).json({ error: "Lesson not found" });
    }
    res.json(lesson);
  });

  app.delete("/api/lessons/:id", async (req, res) => {
    const deleted = await storage.deleteLesson(req.params.id);
    if (!deleted) {
      return res.status(404).json({ error: "Lesson not found" });
    }
    res.json({ success: true });
  });

  // Posts (Blog)
  app.get("/api/posts", async (_req, res) => {
    const posts = await storage.getPosts();
    res.json(posts);
  });

  app.get("/api/posts/:id", async (req, res) => {
    const post = await storage.getPost(req.params.id);
    if (!post) {
      return res.status(404).json({ error: "Post not found" });
    }
    res.json(post);
  });

  app.post("/api/posts", async (req, res) => {
    const result = insertPostSchema.safeParse(req.body);
    if (!result.success) {
      return res.status(400).json({ error: result.error.message });
    }
    const post = await storage.createPost(result.data);
    res.status(201).json(post);
  });

  app.put("/api/posts/:id", async (req, res) => {
    const result = insertPostSchema.safeParse(req.body);
    if (!result.success) {
      return res.status(400).json({ error: result.error.message });
    }
    const post = await storage.updatePost(req.params.id, result.data);
    if (!post) {
      return res.status(404).json({ error: "Post not found" });
    }
    res.json(post);
  });

  app.delete("/api/posts/:id", async (req, res) => {
    const deleted = await storage.deletePost(req.params.id);
    if (!deleted) {
      return res.status(404).json({ error: "Post not found" });
    }
    res.json({ success: true });
  });

  // Stats
  app.get("/api/stats", async (_req, res) => {
    const stats = await storage.getPageViewStats();
    res.json(stats);
  });

  return httpServer;
}
