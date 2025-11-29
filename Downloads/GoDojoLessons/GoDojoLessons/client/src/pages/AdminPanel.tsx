import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useQuery, useMutation } from '@tanstack/react-query';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '@/components/ui/alert-dialog';
import { useToast } from '@/hooks/use-toast';
import { RichTextEditor } from '@/components/RichTextEditor';
import { apiRequest, queryClient } from '@/lib/queryClient';
import { Lock, Plus, Pencil, Trash2, BookOpen, FileText, LogOut, Newspaper } from 'lucide-react';
import type { Topic, Lesson, Post, InsertTopic, InsertLesson, InsertPost } from '@shared/schema';

function AdminLogin({ onLogin }: { onLogin: () => void }) {
  const { t } = useTranslation();
  const [password, setPassword] = useState('');
  const [error, setError] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await apiRequest('POST', '/api/admin/login', { password });
      if (res.ok) {
        sessionStorage.setItem('adminAuth', 'true');
        onLogin();
      } else {
        setError(true);
      }
    } catch {
      setError(true);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4">
      <Card className="w-full max-w-md">
        <CardHeader className="text-center">
          <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-primary/10 flex items-center justify-center">
            <Lock className="w-8 h-8 text-primary" />
          </div>
          <CardTitle>{t('admin.login.title')}</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <Label htmlFor="password">{t('admin.login.password')}</Label>
              <Input
                id="password"
                type="password"
                value={password}
                onChange={(e) => {
                  setPassword(e.target.value);
                  setError(false);
                }}
                className={error ? 'border-destructive' : ''}
                data-testid="input-admin-password"
              />
              {error && (
                <p className="text-sm text-destructive mt-1">{t('admin.login.error')}</p>
              )}
            </div>
            <Button type="submit" className="w-full" data-testid="button-admin-login">
              {t('admin.login.submit')}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}

function TopicForm({ topic, onSave, onCancel }: { 
  topic?: Topic; 
  onSave: (data: InsertTopic) => void;
  onCancel: () => void;
}) {
  const { t } = useTranslation();
  const [formData, setFormData] = useState<InsertTopic>({
    titleRu: topic?.titleRu || '',
    titleEn: topic?.titleEn || '',
    descriptionRu: topic?.descriptionRu || '',
    descriptionEn: topic?.descriptionEn || '',
    order: topic?.order || 0,
    icon: topic?.icon || 'book',
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSave(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <div>
          <Label>{t('admin.topics.titleRu')}</Label>
          <Input
            value={formData.titleRu}
            onChange={(e) => setFormData({ ...formData, titleRu: e.target.value })}
            required
            data-testid="input-topic-title-ru"
          />
        </div>
        <div>
          <Label>{t('admin.topics.titleEn')}</Label>
          <Input
            value={formData.titleEn}
            onChange={(e) => setFormData({ ...formData, titleEn: e.target.value })}
            required
            data-testid="input-topic-title-en"
          />
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <Label>{t('admin.topics.descriptionRu')}</Label>
          <Input
            value={formData.descriptionRu}
            onChange={(e) => setFormData({ ...formData, descriptionRu: e.target.value })}
            required
            data-testid="input-topic-desc-ru"
          />
        </div>
        <div>
          <Label>{t('admin.topics.descriptionEn')}</Label>
          <Input
            value={formData.descriptionEn}
            onChange={(e) => setFormData({ ...formData, descriptionEn: e.target.value })}
            required
            data-testid="input-topic-desc-en"
          />
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <Label>{t('admin.topics.order')}</Label>
          <Input
            type="number"
            value={formData.order}
            onChange={(e) => setFormData({ ...formData, order: parseInt(e.target.value) || 0 })}
            data-testid="input-topic-order"
          />
        </div>
        <div>
          <Label>{t('admin.topics.icon')}</Label>
          <Select value={formData.icon} onValueChange={(v) => setFormData({ ...formData, icon: v })}>
            <SelectTrigger data-testid="select-topic-icon">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="book">Book</SelectItem>
              <SelectItem value="code">Code</SelectItem>
              <SelectItem value="layers">Layers</SelectItem>
              <SelectItem value="zap">Zap</SelectItem>
              <SelectItem value="git">Git</SelectItem>
              <SelectItem value="database">Database</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      <div className="flex justify-end gap-2">
        <Button type="button" variant="outline" onClick={onCancel}>
          {t('admin.topics.cancel')}
        </Button>
        <Button type="submit" data-testid="button-save-topic">
          {t('admin.topics.save')}
        </Button>
      </div>
    </form>
  );
}

function LessonForm({ lesson, topics, onSave, onCancel }: { 
  lesson?: Lesson;
  topics: Topic[];
  onSave: (data: InsertLesson) => void;
  onCancel: () => void;
}) {
  const { t } = useTranslation();
  const [formData, setFormData] = useState<InsertLesson>({
    topicId: lesson?.topicId || '',
    titleRu: lesson?.titleRu || '',
    titleEn: lesson?.titleEn || '',
    contentRu: lesson?.contentRu || '',
    contentEn: lesson?.contentEn || '',
    order: lesson?.order || 0,
  });
  const [activeTab, setActiveTab] = useState<'ru' | 'en'>('ru');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSave(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <Label>{t('admin.lessons.selectTopic')}</Label>
        <Select 
          value={formData.topicId} 
          onValueChange={(v) => setFormData({ ...formData, topicId: v })}
        >
          <SelectTrigger data-testid="select-lesson-topic">
            <SelectValue placeholder={t('admin.lessons.selectTopic')} />
          </SelectTrigger>
          <SelectContent>
            {topics.map((topic) => (
              <SelectItem key={topic.id} value={topic.id}>
                {topic.titleRu}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <Label>{t('admin.lessons.titleRu')}</Label>
          <Input
            value={formData.titleRu}
            onChange={(e) => setFormData({ ...formData, titleRu: e.target.value })}
            required
            data-testid="input-lesson-title-ru"
          />
        </div>
        <div>
          <Label>{t('admin.lessons.titleEn')}</Label>
          <Input
            value={formData.titleEn}
            onChange={(e) => setFormData({ ...formData, titleEn: e.target.value })}
            required
            data-testid="input-lesson-title-en"
          />
        </div>
      </div>

      <div>
        <Label>{t('admin.lessons.order')}</Label>
        <Input
          type="number"
          value={formData.order}
          onChange={(e) => setFormData({ ...formData, order: parseInt(e.target.value) || 0 })}
          className="w-32"
          data-testid="input-lesson-order"
        />
      </div>

      <div>
        <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as 'ru' | 'en')}>
          <TabsList>
            <TabsTrigger value="ru">{t('admin.lessons.contentRu')}</TabsTrigger>
            <TabsTrigger value="en">{t('admin.lessons.contentEn')}</TabsTrigger>
          </TabsList>
          <TabsContent value="ru" className="mt-4">
            <RichTextEditor
              content={formData.contentRu}
              onChange={(content) => setFormData({ ...formData, contentRu: content })}
              placeholder="Содержание урока на русском..."
            />
          </TabsContent>
          <TabsContent value="en" className="mt-4">
            <RichTextEditor
              content={formData.contentEn}
              onChange={(content) => setFormData({ ...formData, contentEn: content })}
              placeholder="Lesson content in English..."
            />
          </TabsContent>
        </Tabs>
      </div>

      <div className="flex justify-end gap-2">
        <Button type="button" variant="outline" onClick={onCancel}>
          {t('admin.lessons.cancel')}
        </Button>
        <Button type="submit" data-testid="button-save-lesson">
          {t('admin.lessons.save')}
        </Button>
      </div>
    </form>
  );
}

function PostForm({ post, onSave, onCancel }: { 
  post?: Post;
  onSave: (data: InsertPost) => void;
  onCancel: () => void;
}) {
  const { t } = useTranslation();
  const [formData, setFormData] = useState<InsertPost>({
    titleRu: post?.titleRu || '',
    titleEn: post?.titleEn || '',
    contentRu: post?.contentRu || '',
    contentEn: post?.contentEn || '',
    order: post?.order || 0,
  });
  const [activeTab, setActiveTab] = useState<'ru' | 'en'>('ru');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSave(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <div>
          <Label>{t('admin.posts.titleRu')}</Label>
          <Input
            value={formData.titleRu}
            onChange={(e) => setFormData({ ...formData, titleRu: e.target.value })}
            required
            data-testid="input-post-title-ru"
          />
        </div>
        <div>
          <Label>{t('admin.posts.titleEn')}</Label>
          <Input
            value={formData.titleEn}
            onChange={(e) => setFormData({ ...formData, titleEn: e.target.value })}
            required
            data-testid="input-post-title-en"
          />
        </div>
      </div>

      <div>
        <Label>{t('admin.posts.order')}</Label>
        <Input
          type="number"
          value={formData.order}
          onChange={(e) => setFormData({ ...formData, order: parseInt(e.target.value) || 0 })}
          className="w-32"
          data-testid="input-post-order"
        />
      </div>

      <div>
        <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as 'ru' | 'en')}>
          <TabsList>
            <TabsTrigger value="ru">{t('admin.posts.contentRu')}</TabsTrigger>
            <TabsTrigger value="en">{t('admin.posts.contentEn')}</TabsTrigger>
          </TabsList>
          <TabsContent value="ru" className="mt-4">
            <RichTextEditor
              content={formData.contentRu}
              onChange={(content) => setFormData({ ...formData, contentRu: content })}
              placeholder="Содержание поста на русском..."
            />
          </TabsContent>
          <TabsContent value="en" className="mt-4">
            <RichTextEditor
              content={formData.contentEn}
              onChange={(content) => setFormData({ ...formData, contentEn: content })}
              placeholder="Post content in English..."
            />
          </TabsContent>
        </Tabs>
      </div>

      <div className="flex justify-end gap-2">
        <Button type="button" variant="outline" onClick={onCancel}>
          {t('admin.posts.cancel')}
        </Button>
        <Button type="submit" data-testid="button-save-post">
          {t('admin.posts.save')}
        </Button>
      </div>
    </form>
  );
}

function StatsSection() {
  const { t } = useTranslation();
  const { data: stats, isLoading } = useQuery({
    queryKey: ['/api/stats'],
  });

  if (isLoading) {
    return <div className="animate-pulse text-muted-foreground">Loading...</div>;
  }

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>{t('admin.stats.uniqueVisitors')}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-4xl font-bold">{stats?.uniqueVisits || 0}</div>
          <p className="text-sm text-muted-foreground mt-2">{t('admin.stats.uniqueVisitorsDescription')}</p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>{t('admin.stats.totalVisits')}</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-3xl font-bold">{stats?.totalVisits || 0}</div>
          <p className="text-sm text-muted-foreground mt-2">{t('admin.stats.totalVisitsDescription')}</p>
        </CardContent>
      </Card>
    </div>
  );
}

function AdminDashboard({ onLogout }: { onLogout: () => void }) {
  const { t, i18n } = useTranslation();
  const { toast } = useToast();
  const lang = i18n.language;

  const [editingTopic, setEditingTopic] = useState<Topic | null>(null);
  const [editingLesson, setEditingLesson] = useState<Lesson | null>(null);
  const [editingPost, setEditingPost] = useState<Post | null>(null);
  const [isTopicDialogOpen, setIsTopicDialogOpen] = useState(false);
  const [isLessonDialogOpen, setIsLessonDialogOpen] = useState(false);
  const [isPostDialogOpen, setIsPostDialogOpen] = useState(false);

  const { data: topics = [] } = useQuery<Topic[]>({
    queryKey: ['/api/topics'],
  });

  const { data: lessons = [] } = useQuery<Lesson[]>({
    queryKey: ['/api/lessons'],
  });

  const { data: posts = [] } = useQuery<Post[]>({
    queryKey: ['/api/posts'],
  });

  const createTopicMutation = useMutation({
    mutationFn: (data: InsertTopic) => apiRequest('POST', '/api/topics', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['/api/topics'] });
      setIsTopicDialogOpen(false);
      toast({ title: t('admin.success.topicCreated') });
    },
  });

  const updateTopicMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: InsertTopic }) => 
      apiRequest('PUT', `/api/topics/${id}`, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['/api/topics'] });
      setEditingTopic(null);
      toast({ title: t('admin.success.topicUpdated') });
    },
  });

  const deleteTopicMutation = useMutation({
    mutationFn: (id: string) => apiRequest('DELETE', `/api/topics/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['/api/topics'] });
      queryClient.invalidateQueries({ queryKey: ['/api/lessons'] });
      toast({ title: t('admin.success.topicDeleted') });
    },
  });

  const createLessonMutation = useMutation({
    mutationFn: (data: InsertLesson) => apiRequest('POST', '/api/lessons', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['/api/lessons'] });
      setIsLessonDialogOpen(false);
      toast({ title: t('admin.success.lessonCreated') });
    },
  });

  const updateLessonMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: InsertLesson }) => 
      apiRequest('PUT', `/api/lessons/${id}`, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['/api/lessons'] });
      setEditingLesson(null);
      toast({ title: t('admin.success.lessonUpdated') });
    },
  });

  const deleteLessonMutation = useMutation({
    mutationFn: (id: string) => apiRequest('DELETE', `/api/lessons/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['/api/lessons'] });
      toast({ title: t('admin.success.lessonDeleted') });
    },
  });

  const createPostMutation = useMutation({
    mutationFn: (data: InsertPost) => apiRequest('POST', '/api/posts', data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['/api/posts'] });
      setIsPostDialogOpen(false);
      toast({ title: t('admin.success.postCreated') });
    },
  });

  const updatePostMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: InsertPost }) => 
      apiRequest('PUT', `/api/posts/${id}`, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['/api/posts'] });
      setEditingPost(null);
      toast({ title: t('admin.success.postUpdated') });
    },
  });

  const deletePostMutation = useMutation({
    mutationFn: (id: string) => apiRequest('DELETE', `/api/posts/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['/api/posts'] });
      toast({ title: t('admin.success.postDeleted') });
    },
  });

  return (
    <div className="min-h-screen bg-background">
      <header className="sticky top-0 z-50 border-b border-border bg-background/95 backdrop-blur">
        <div className="flex h-16 items-center justify-between px-4 md:px-6">
          <h1 className="text-xl font-bold">{t('admin.title')}</h1>
          <Button variant="ghost" onClick={onLogout} data-testid="button-admin-logout">
            <LogOut className="mr-2 h-4 w-4" />
            Выход
          </Button>
        </div>
      </header>

      <main className="mx-auto max-w-6xl px-4 py-8 md:px-6">
        <Tabs defaultValue="stats" className="space-y-6">
          <TabsList>
            <TabsTrigger value="stats" className="gap-2">
              <div className="h-4 w-4">📊</div>
              {t('admin.sidebar.stats')}
            </TabsTrigger>
            <TabsTrigger value="topics" className="gap-2">
              <BookOpen className="h-4 w-4" />
              {t('admin.sidebar.topics')}
            </TabsTrigger>
            <TabsTrigger value="lessons" className="gap-2">
              <FileText className="h-4 w-4" />
              {t('admin.sidebar.lessons')}
            </TabsTrigger>
            <TabsTrigger value="posts" className="gap-2">
              <Newspaper className="h-4 w-4" />
              {t('admin.sidebar.posts')}
            </TabsTrigger>
          </TabsList>

          <TabsContent value="stats" className="space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold">{t('admin.stats.title')}</h2>
            </div>
            <StatsSection />
          </TabsContent>

          <TabsContent value="topics" className="space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold">{t('admin.topics.title')}</h2>
              <Dialog open={isTopicDialogOpen} onOpenChange={setIsTopicDialogOpen}>
                <DialogTrigger asChild>
                  <Button data-testid="button-create-topic">
                    <Plus className="mr-2 h-4 w-4" />
                    {t('admin.topics.create')}
                  </Button>
                </DialogTrigger>
                <DialogContent className="max-w-2xl">
                  <DialogHeader>
                    <DialogTitle>{t('admin.topics.create')}</DialogTitle>
                  </DialogHeader>
                  <TopicForm
                    onSave={(data) => createTopicMutation.mutate(data)}
                    onCancel={() => setIsTopicDialogOpen(false)}
                  />
                </DialogContent>
              </Dialog>
            </div>

            <div className="grid gap-4">
              {topics.sort((a, b) => a.order - b.order).map((topic) => (
                <Card key={topic.id} data-testid={`card-admin-topic-${topic.id}`}>
                  <CardContent className="flex items-center justify-between p-4">
                    <div>
                      <h3 className="font-semibold">{lang === 'ru' ? topic.titleRu : topic.titleEn}</h3>
                      <p className="text-sm text-muted-foreground">
                        {lang === 'ru' ? topic.descriptionRu : topic.descriptionEn}
                      </p>
                      <p className="text-xs text-muted-foreground mt-1">
                        Порядок: {topic.order} | ID: {topic.id}
                      </p>
                    </div>
                    <div className="flex gap-2">
                      <Dialog open={editingTopic?.id === topic.id} onOpenChange={(open) => !open && setEditingTopic(null)}>
                        <DialogTrigger asChild>
                          <Button 
                            variant="outline" 
                            size="icon"
                            onClick={() => setEditingTopic(topic)}
                            data-testid={`button-edit-topic-${topic.id}`}
                          >
                            <Pencil className="h-4 w-4" />
                          </Button>
                        </DialogTrigger>
                        <DialogContent className="max-w-2xl">
                          <DialogHeader>
                            <DialogTitle>{t('admin.topics.edit')}</DialogTitle>
                          </DialogHeader>
                          <TopicForm
                            topic={editingTopic || undefined}
                            onSave={(data) => updateTopicMutation.mutate({ id: topic.id, data })}
                            onCancel={() => setEditingTopic(null)}
                          />
                        </DialogContent>
                      </Dialog>

                      <AlertDialog>
                        <AlertDialogTrigger asChild>
                          <Button variant="destructive" size="icon" data-testid={`button-delete-topic-${topic.id}`}>
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </AlertDialogTrigger>
                        <AlertDialogContent>
                          <AlertDialogHeader>
                            <AlertDialogTitle>Удалить тему?</AlertDialogTitle>
                            <AlertDialogDescription>
                              Это действие нельзя отменить. Все уроки в этой теме также будут удалены.
                            </AlertDialogDescription>
                          </AlertDialogHeader>
                          <AlertDialogFooter>
                            <AlertDialogCancel>Отмена</AlertDialogCancel>
                            <AlertDialogAction onClick={() => deleteTopicMutation.mutate(topic.id)}>
                              Удалить
                            </AlertDialogAction>
                          </AlertDialogFooter>
                        </AlertDialogContent>
                      </AlertDialog>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          <TabsContent value="lessons" className="space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold">{t('admin.lessons.title')}</h2>
              <Dialog open={isLessonDialogOpen} onOpenChange={setIsLessonDialogOpen}>
                <DialogTrigger asChild>
                  <Button data-testid="button-create-lesson">
                    <Plus className="mr-2 h-4 w-4" />
                    {t('admin.lessons.create')}
                  </Button>
                </DialogTrigger>
                <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
                  <DialogHeader>
                    <DialogTitle>{t('admin.lessons.create')}</DialogTitle>
                  </DialogHeader>
                  <LessonForm
                    topics={topics}
                    onSave={(data) => createLessonMutation.mutate(data)}
                    onCancel={() => setIsLessonDialogOpen(false)}
                  />
                </DialogContent>
              </Dialog>
            </div>

            <div className="grid gap-4">
              {topics.sort((a, b) => a.order - b.order).map((topic) => {
                const topicLessons = lessons
                  .filter((l) => l.topicId === topic.id)
                  .sort((a, b) => a.order - b.order);

                if (topicLessons.length === 0) return null;

                return (
                  <div key={topic.id}>
                    <h3 className="font-semibold mb-3 text-muted-foreground">
                      {lang === 'ru' ? topic.titleRu : topic.titleEn}
                    </h3>
                    <div className="space-y-2">
                      {topicLessons.map((lesson) => (
                        <Card key={lesson.id} data-testid={`card-admin-lesson-${lesson.id}`}>
                          <CardContent className="flex items-center justify-between p-4">
                            <div>
                              <h4 className="font-medium">
                                {lesson.order}. {lang === 'ru' ? lesson.titleRu : lesson.titleEn}
                              </h4>
                              <p className="text-xs text-muted-foreground mt-1">
                                ID: {lesson.id}
                              </p>
                            </div>
                            <div className="flex gap-2">
                              <Dialog open={editingLesson?.id === lesson.id} onOpenChange={(open) => !open && setEditingLesson(null)}>
                                <DialogTrigger asChild>
                                  <Button 
                                    variant="outline" 
                                    size="icon"
                                    onClick={() => setEditingLesson(lesson)}
                                    data-testid={`button-edit-lesson-${lesson.id}`}
                                  >
                                    <Pencil className="h-4 w-4" />
                                  </Button>
                                </DialogTrigger>
                                <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
                                  <DialogHeader>
                                    <DialogTitle>{t('admin.lessons.edit')}</DialogTitle>
                                  </DialogHeader>
                                  <LessonForm
                                    lesson={editingLesson || undefined}
                                    topics={topics}
                                    onSave={(data) => updateLessonMutation.mutate({ id: lesson.id, data })}
                                    onCancel={() => setEditingLesson(null)}
                                  />
                                </DialogContent>
                              </Dialog>

                              <AlertDialog>
                                <AlertDialogTrigger asChild>
                                  <Button variant="destructive" size="icon" data-testid={`button-delete-lesson-${lesson.id}`}>
                                    <Trash2 className="h-4 w-4" />
                                  </Button>
                                </AlertDialogTrigger>
                                <AlertDialogContent>
                                  <AlertDialogHeader>
                                    <AlertDialogTitle>Удалить урок?</AlertDialogTitle>
                                    <AlertDialogDescription>
                                      Это действие нельзя отменить.
                                    </AlertDialogDescription>
                                  </AlertDialogHeader>
                                  <AlertDialogFooter>
                                    <AlertDialogCancel>Отмена</AlertDialogCancel>
                                    <AlertDialogAction onClick={() => deleteLessonMutation.mutate(lesson.id)}>
                                      Удалить
                                    </AlertDialogAction>
                                  </AlertDialogFooter>
                                </AlertDialogContent>
                              </AlertDialog>
                            </div>
                          </CardContent>
                        </Card>
                      ))}
                    </div>
                  </div>
                );
              })}
            </div>
          </TabsContent>

          <TabsContent value="posts" className="space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-2xl font-bold">{t('admin.posts.title')}</h2>
              <Dialog open={isPostDialogOpen} onOpenChange={setIsPostDialogOpen}>
                <DialogTrigger asChild>
                  <Button data-testid="button-create-post">
                    <Plus className="mr-2 h-4 w-4" />
                    {t('admin.posts.create')}
                  </Button>
                </DialogTrigger>
                <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
                  <DialogHeader>
                    <DialogTitle>{t('admin.posts.create')}</DialogTitle>
                  </DialogHeader>
                  <PostForm
                    onSave={(data) => createPostMutation.mutate(data)}
                    onCancel={() => setIsPostDialogOpen(false)}
                  />
                </DialogContent>
              </Dialog>
            </div>

            <div className="space-y-4">
              {posts.sort((a, b) => b.order - a.order).map((post) => (
                <Card key={post.id} data-testid={`card-admin-post-${post.id}`}>
                  <CardContent className="flex items-center justify-between p-4">
                    <div className="flex-1">
                      <h3 className="font-semibold">{lang === 'ru' ? post.titleRu : post.titleEn}</h3>
                      <p className="text-xs text-muted-foreground mt-1">
                        {new Date(post.createdAt).toLocaleDateString(lang === 'ru' ? 'ru-RU' : 'en-US', {
                          year: 'numeric',
                          month: 'long',
                          day: 'numeric',
                        })} | ID: {post.id}
                      </p>
                    </div>
                    <div className="flex gap-2">
                      <Dialog open={editingPost?.id === post.id} onOpenChange={(open) => !open && setEditingPost(null)}>
                        <DialogTrigger asChild>
                          <Button 
                            variant="outline" 
                            size="icon"
                            onClick={() => setEditingPost(post)}
                            data-testid={`button-edit-post-${post.id}`}
                          >
                            <Pencil className="h-4 w-4" />
                          </Button>
                        </DialogTrigger>
                        <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
                          <DialogHeader>
                            <DialogTitle>{t('admin.posts.edit')}</DialogTitle>
                          </DialogHeader>
                          <PostForm
                            post={editingPost || undefined}
                            onSave={(data) => updatePostMutation.mutate({ id: post.id, data })}
                            onCancel={() => setEditingPost(null)}
                          />
                        </DialogContent>
                      </Dialog>

                      <AlertDialog>
                        <AlertDialogTrigger asChild>
                          <Button variant="destructive" size="icon" data-testid={`button-delete-post-${post.id}`}>
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </AlertDialogTrigger>
                        <AlertDialogContent>
                          <AlertDialogHeader>
                            <AlertDialogTitle>Удалить пост?</AlertDialogTitle>
                            <AlertDialogDescription>
                              Это действие нельзя отменить.
                            </AlertDialogDescription>
                          </AlertDialogHeader>
                          <AlertDialogFooter>
                            <AlertDialogCancel>Отмена</AlertDialogCancel>
                            <AlertDialogAction onClick={() => deletePostMutation.mutate(post.id)}>
                              Удалить
                            </AlertDialogAction>
                          </AlertDialogFooter>
                        </AlertDialogContent>
                      </AlertDialog>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
}

export default function AdminPanel() {
  const [isAuthenticated, setIsAuthenticated] = useState(() => {
    return sessionStorage.getItem('adminAuth') === 'true';
  });

  const handleLogout = () => {
    sessionStorage.removeItem('adminAuth');
    setIsAuthenticated(false);
  };

  if (!isAuthenticated) {
    return <AdminLogin onLogin={() => setIsAuthenticated(true)} />;
  }

  return <AdminDashboard onLogout={handleLogout} />;
}
