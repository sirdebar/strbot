import { useTranslation } from 'react-i18next';
import { Link, useParams } from 'wouter';
import { useQuery } from '@tanstack/react-query';
import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { ArrowLeft, ChevronLeft, ChevronRight } from 'lucide-react';
import type { Lesson, Topic } from '@shared/schema';

export default function LessonPage() {
  const { t, i18n } = useTranslation();
  const lang = i18n.language;
  const { id } = useParams<{ id: string }>();

  const { data: lesson, isLoading: lessonLoading } = useQuery<Lesson>({
    queryKey: ['/api/lessons', id],
  });

  const { data: topic, isLoading: topicLoading } = useQuery<Topic>({
    queryKey: ['/api/topics', lesson?.topicId],
    enabled: !!lesson?.topicId,
  });

  const { data: topicLessons } = useQuery<Lesson[]>({
    queryKey: ['/api/topics', lesson?.topicId, 'lessons'],
    enabled: !!lesson?.topicId,
  });

  if (lessonLoading || topicLoading) {
    return (
      <div className="container max-w-4xl mx-auto px-4 py-12">
        <Skeleton className="h-8 w-32 mb-8" />
        <Skeleton className="h-10 w-3/4 mb-8" />
        <div className="space-y-4">
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-2/3" />
        </div>
      </div>
    );
  }

  if (!lesson) {
    return (
      <div className="container max-w-4xl mx-auto px-4 py-12 text-center">
        <p className="text-lg text-muted-foreground">Урок не найден</p>
        <Link href="/">
          <Button className="mt-4">
            <ArrowLeft className="mr-2 h-4 w-4" />
            {t('nav.topics')}
          </Button>
        </Link>
      </div>
    );
  }

  const sortedLessons = topicLessons?.sort((a, b) => a.order - b.order) || [];
  const currentIndex = sortedLessons.findIndex(l => l.id === lesson.id);
  const prevLesson = currentIndex > 0 ? sortedLessons[currentIndex - 1] : null;
  const nextLesson = currentIndex < sortedLessons.length - 1 ? sortedLessons[currentIndex + 1] : null;

  const content = lang === 'ru' ? lesson.contentRu : lesson.contentEn;
  const title = lang === 'ru' ? lesson.titleRu : lesson.titleEn;

  return (
    <div className="min-h-screen flex flex-col">
      <div className="container max-w-4xl mx-auto px-4 py-12 flex-1">
        {topic && (
          <Link 
            href={`/topic/${topic.id}`} 
            className="inline-flex items-center text-muted-foreground hover:text-foreground mb-8 transition-colors"
            data-testid="link-back-to-topic"
          >
            <ArrowLeft className="mr-2 h-4 w-4" />
            {lang === 'ru' ? topic.titleRu : topic.titleEn}
          </Link>
        )}

        {sortedLessons.length > 0 && (
          <div className="flex flex-wrap gap-2 mb-8">
            {sortedLessons.map((l, index) => (
              <Link key={l.id} href={`/lesson/${l.id}`}>
                <div
                  className={`w-10 h-10 rounded-md flex items-center justify-center font-medium text-sm cursor-pointer transition-colors ${
                    l.id === lesson.id
                      ? 'bg-primary text-primary-foreground'
                      : 'bg-muted text-muted-foreground hover:bg-accent'
                  }`}
                  title={lang === 'ru' ? l.titleRu : l.titleEn}
                  data-testid={`button-lesson-nav-${l.id}`}
                >
                  {index + 1}
                </div>
              </Link>
            ))}
          </div>
        )}

        <article className="mb-12">
          <h1 className="text-3xl md:text-4xl font-bold mb-8">
            {currentIndex + 1}. {title}
          </h1>

          {content ? (
            <div 
              className="prose prose-lg dark:prose-invert max-w-none [&_img]:max-w-full [&_img]:rounded-lg [&_img]:my-4 [&_img]:h-auto"
              dangerouslySetInnerHTML={{ __html: content }}
            />
          ) : (
            <p className="text-muted-foreground italic">{t('lesson.noContent')}</p>
          )}
        </article>

        <nav className="flex items-center justify-between gap-4 pt-8 border-t border-border">
          {prevLesson ? (
            <Link href={`/lesson/${prevLesson.id}`}>
              <Button variant="outline" data-testid="button-prev-lesson">
                <ChevronLeft className="mr-2 h-4 w-4" />
                {t('lesson.prevLesson')}
              </Button>
            </Link>
          ) : (
            <div />
          )}

          {nextLesson ? (
            <Link href={`/lesson/${nextLesson.id}`}>
              <Button data-testid="button-next-lesson">
                {t('lesson.nextLesson')}
                <ChevronRight className="ml-2 h-4 w-4" />
              </Button>
            </Link>
          ) : (
            <Link href={topic ? `/topic/${topic.id}` : '/'}>
              <Button variant="outline" data-testid="button-back-to-lessons">
                {t('lesson.backToTopic')}
              </Button>
            </Link>
          )}
        </nav>
      </div>

      <footer className="py-8 px-4 border-t border-border">
        <div className="container max-w-4xl mx-auto text-center text-muted-foreground text-sm">
          {t('footer.copyright')}
        </div>
      </footer>
    </div>
  );
}
