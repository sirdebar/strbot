import { useTranslation } from 'react-i18next';
import { Link, useRoute } from 'wouter';
import { useQuery } from '@tanstack/react-query';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { ArrowLeft } from 'lucide-react';
import type { Post } from '@shared/schema';

export default function BlogPost() {
  const { t, i18n } = useTranslation();
  const lang = i18n.language as 'ru' | 'en';
  const [, params] = useRoute('/blog/:id');
  const postId = params?.id;

  const { data: post, isLoading } = useQuery<Post>({
    queryKey: [`/api/posts/${postId}`],
    enabled: !!postId,
  });

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-pulse text-muted-foreground">Loading...</div>
      </div>
    );
  }

  if (!post) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center gap-4">
        <p className="text-muted-foreground">Post not found</p>
        <Link href="/blog">
          <Button variant="outline">
            <ArrowLeft className="mr-2 h-4 w-4" />
            {t('blog.backToBlog')}
          </Button>
        </Link>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <div className="mx-auto max-w-3xl px-4 py-12 md:px-6">
        <Link href="/blog" className="mb-8 block">
          <Button variant="outline" className="gap-2">
            <ArrowLeft className="h-4 w-4" />
            {t('blog.backToBlog')}
          </Button>
        </Link>

        <Card>
          <CardHeader className="pb-4">
            <h1 className="text-4xl font-bold mb-4">
              {lang === 'ru' ? post.titleRu : post.titleEn}
            </h1>
            <p className="text-muted-foreground">
              {new Date(post.createdAt).toLocaleDateString(lang === 'ru' ? 'ru-RU' : 'en-US', {
                year: 'numeric',
                month: 'long',
                day: 'numeric',
              })}
            </p>
          </CardHeader>
          <CardContent>
            <div 
              className="prose prose-sm dark:prose-invert max-w-none"
              dangerouslySetInnerHTML={{
                __html: lang === 'ru' ? post.contentRu : post.contentEn,
              }}
            />
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
