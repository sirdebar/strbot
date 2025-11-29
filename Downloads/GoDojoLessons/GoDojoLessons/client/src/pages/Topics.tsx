import { useTranslation } from 'react-i18next';
import { Link } from 'wouter';
import { useQuery } from '@tanstack/react-query';
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { ChevronRight, BookOpen, Code2, Layers, Zap, GitBranch, Database } from 'lucide-react';
import type { Topic, Lesson } from '@shared/schema';

const iconMap: Record<string, React.ElementType> = {
  'book': BookOpen,
  'code': Code2,
  'layers': Layers,
  'zap': Zap,
  'git': GitBranch,
  'database': Database,
};

export default function Topics() {
  const { t, i18n } = useTranslation();
  const lang = i18n.language;

  const { data: topics, isLoading: topicsLoading } = useQuery<Topic[]>({
    queryKey: ['/api/topics'],
  });

  const { data: lessons } = useQuery<Lesson[]>({
    queryKey: ['/api/lessons'],
  });

  const getLessonCount = (topicId: string) => {
    return lessons?.filter(l => l.topicId === topicId).length || 0;
  };

  const getTopicIcon = (icon?: string) => {
    const Icon = icon ? iconMap[icon] || BookOpen : BookOpen;
    return Icon;
  };

  if (topicsLoading) {
    return (
      <div className="container max-w-6xl mx-auto px-4 py-12">
        <div className="text-center mb-12">
          <Skeleton className="h-10 w-64 mx-auto mb-4" />
          <Skeleton className="h-6 w-96 mx-auto" />
        </div>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <Card key={i}>
              <CardHeader>
                <Skeleton className="h-12 w-12 rounded-lg mb-4" />
                <Skeleton className="h-6 w-3/4" />
              </CardHeader>
              <CardContent>
                <Skeleton className="h-4 w-full mb-2" />
                <Skeleton className="h-4 w-2/3" />
              </CardContent>
              <CardFooter>
                <Skeleton className="h-10 w-full" />
              </CardFooter>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="container max-w-6xl mx-auto px-4 py-12">
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold mb-4">{t('topics.title')}</h1>
        <p className="text-lg text-muted-foreground">{t('topics.subtitle')}</p>
      </div>

      {!topics || topics.length === 0 ? (
        <div className="text-center py-20">
          <BookOpen className="w-16 h-16 mx-auto text-muted-foreground/50 mb-4" />
          <p className="text-lg text-muted-foreground">{t('topics.noTopics')}</p>
        </div>
      ) : (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {topics
            .sort((a, b) => a.order - b.order)
            .map((topic) => {
              const Icon = getTopicIcon(topic.icon);
              const lessonCount = getLessonCount(topic.id);
              
              return (
                <Card 
                  key={topic.id} 
                  className="hover-elevate group flex flex-col"
                  data-testid={`card-topic-${topic.id}`}
                >
                  <CardHeader>
                    <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4 group-hover:bg-primary/20 transition-colors">
                      <Icon className="w-6 h-6 text-primary" />
                    </div>
                    <CardTitle className="text-xl">
                      {lang === 'ru' ? topic.titleRu : topic.titleEn}
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="flex-1">
                    <p className="text-muted-foreground">
                      {lang === 'ru' ? topic.descriptionRu : topic.descriptionEn}
                    </p>
                    <p className="text-sm text-muted-foreground mt-4">
                      {lessonCount} {t('topics.lessonsCount')}
                    </p>
                  </CardContent>
                  <CardFooter>
                    <Link href={`/topic/${topic.id}`} className="w-full">
                      <Button className="w-full" data-testid={`button-start-topic-${topic.id}`}>
                        {t('topics.startLearning')}
                        <ChevronRight className="ml-2 h-4 w-4" />
                      </Button>
                    </Link>
                  </CardFooter>
                </Card>
              );
            })}
        </div>
      )}

      <footer className="mt-20 pt-8 border-t border-border text-center text-muted-foreground text-sm">
        {t('footer.copyright')}
      </footer>
    </div>
  );
}
