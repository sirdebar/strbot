import { useTranslation } from 'react-i18next';
import { Link } from 'wouter';
import { useQuery } from '@tanstack/react-query';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ArrowRight } from 'lucide-react';
import type { Post } from '@shared/schema';

export default function Blog() {
  const { t, i18n } = useTranslation();
  const lang = i18n.language as 'ru' | 'en';

  const { data: posts = [], isLoading } = useQuery<Post[]>({
    queryKey: ['/api/posts'],
  });

  return (
    <div className="min-h-screen bg-background">
      <div className="mx-auto max-w-4xl px-4 py-12 md:px-6">
        <div className="mb-12 text-center">
          <h1 className="text-4xl font-bold mb-2">{t('blog.title')}</h1>
          <p className="text-lg text-muted-foreground">{t('blog.subtitle')}</p>
        </div>

        {isLoading ? (
          <div className="flex justify-center py-12">
            <div className="animate-pulse text-muted-foreground">{t('common.loading', 'Загрузка...')}</div>
          </div>
        ) : posts.length === 0 ? (
          <Card>
            <CardContent className="flex flex-col items-center justify-center py-12">
              <p className="text-muted-foreground">{t('blog.noPosts')}</p>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-6">
            {posts.sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()).map((post) => (
              <Card key={post.id} className="overflow-hidden hover-elevate transition-all">
                <CardHeader className="pb-3">
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1">
                      <p className="text-sm text-muted-foreground mb-2">
                        {new Date(post.createdAt).toLocaleDateString(lang === 'ru' ? 'ru-RU' : 'en-US', {
                          year: 'numeric',
                          month: 'long',
                          day: 'numeric',
                        })}
                      </p>
                      <CardTitle className="text-2xl mb-2">
                        {lang === 'ru' ? post.titleRu : post.titleEn}
                      </CardTitle>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div 
                    className="prose prose-sm dark:prose-invert max-w-none mb-4 line-clamp-3"
                    dangerouslySetInnerHTML={{
                      __html: lang === 'ru' ? post.contentRu : post.contentEn,
                    }}
                  />
                  <Link href={`/blog/${post.id}`}>
                    <Button variant="outline" className="group">
                      {t('blog.readMore')}
                      <ArrowRight className="ml-2 h-4 w-4 group-hover:translate-x-1 transition-transform" />
                    </Button>
                  </Link>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
