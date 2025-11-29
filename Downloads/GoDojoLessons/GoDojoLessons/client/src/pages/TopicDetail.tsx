import { useTranslation } from 'react-i18next';
import { Link, useParams } from 'wouter';
import { useQuery } from '@tanstack/react-query';
import { Button } from '@/components/ui/button';
import { Card } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';
import { ArrowLeft, ChevronRight, BookOpen } from 'lucide-react';
import type { Topic, Lesson } from '@shared/schema';

export default function TopicDetail() {
  const { t, i18n } = useTranslation();
  const lang = i18n.language;
  const { id } = useParams<{ id: string }>();

  const { data: topic, isLoading: topicLoading } = useQuery<Topic>({
    queryKey: ['/api/topics', id],
  });

  const { data: lessons, isLoading: lessonsLoading } = useQuery<Lesson[]>({
    queryKey: ['/api/topics', id, 'lessons'],
  });

  if (topicLoading || lessonsLoading) {
    return (
      <div className="container max-w-4xl mx-auto px-4 py-12">
        <Skeleton className="h-8 w-32 mb-8" />
        <Skeleton className="h-10 w-64 mb-4" />
        <Skeleton className="h-6 w-96 mb-8" />
        <div className="space-y-4">
          {[1, 2, 3, 4].map((i) => (
            <Skeleton key={i} className="h-20 w-full" />
          ))}
        </div>
      </div>
    );
  }

  if (!topic) {
    return (
      <div className="container max-w-4xl mx-auto px-4 py-12 text-center">
        <p className="text-lg text-muted-foreground">Тема не найдена</p>
        <Link href="/">
          <Button className="mt-4">
            <ArrowLeft className="mr-2 h-4 w-4" />
            {t('lesson.backToTopic')}
          </Button>
        </Link>
      </div>
    );
  }

  const sortedLessons = lessons?.sort((a, b) => a.order - b.order) || [];

  return (
    <div className="container max-w-4xl mx-auto px-4 py-12">
      <Link href="/" className="inline-flex items-center text-muted-foreground hover:text-foreground mb-8 transition-colors">
        <ArrowLeft className="mr-2 h-4 w-4" />
        {t('nav.topics')}
      </Link>

      <div className="mb-12">
        <h1 className="text-4xl font-bold mb-4">
          {lang === 'ru' ? topic.titleRu : topic.titleEn}
        </h1>
        <p className="text-lg text-muted-foreground">
          {lang === 'ru' ? topic.descriptionRu : topic.descriptionEn}
        </p>
      </div>

      {sortedLessons.length === 0 ? (
        <div className="text-center py-20">
          <BookOpen className="w-16 h-16 mx-auto text-muted-foreground/50 mb-4" />
          <p className="text-lg text-muted-foreground">Уроки скоро появятся...</p>
        </div>
      ) : (
        <div className="space-y-4">
          {sortedLessons.map((lesson, index) => (
            <Link key={lesson.id} href={`/lesson/${lesson.id}`}>
              <Card 
                className="hover-elevate p-4 flex items-center gap-4 cursor-pointer"
                data-testid={`card-lesson-${lesson.id}`}
              >
                <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center font-bold text-primary flex-shrink-0">
                  {index + 1}
                </div>
                <div className="flex-1 min-w-0">
                  <h3 className="font-semibold truncate">
                    {lang === 'ru' ? lesson.titleRu : lesson.titleEn}
                  </h3>
                </div>
                <ChevronRight className="h-5 w-5 text-muted-foreground flex-shrink-0" />
              </Card>
            </Link>
          ))}
        </div>
      )}

      <footer className="mt-20 pt-8 border-t border-border text-center text-muted-foreground text-sm">
        {t('footer.copyright')}
      </footer>
    </div>
  );
}
