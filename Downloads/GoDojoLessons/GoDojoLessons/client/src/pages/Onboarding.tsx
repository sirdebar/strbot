import { useTranslation } from 'react-i18next';
import { Link } from 'wouter';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { 
  Code2, 
  Zap, 
  Server, 
  ChevronRight,
  Sword,
  Target,
  Shield
} from 'lucide-react';

export default function Onboarding() {
  const { t } = useTranslation();

  const skills = [
    {
      icon: Code2,
      title: t('onboarding.skills.skill1.title'),
      description: t('onboarding.skills.skill1.description'),
    },
    {
      icon: Zap,
      title: t('onboarding.skills.skill2.title'),
      description: t('onboarding.skills.skill2.description'),
    },
    {
      icon: Server,
      title: t('onboarding.skills.skill3.title'),
      description: t('onboarding.skills.skill3.description'),
    },
  ];

  const pathSteps = [
    { title: 'Введение', titleEn: 'Introduction' },
    { title: 'Типы данных', titleEn: 'Data Types' },
    { title: 'Функции', titleEn: 'Functions' },
    { title: 'ООП', titleEn: 'OOP' },
    { title: 'Конкурентность', titleEn: 'Concurrency' },
  ];

  return (
    <div className="min-h-screen">
      <section className="relative min-h-[600px] flex items-center justify-center overflow-hidden py-20 px-4">
        <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-primary/10" />
        <div className="absolute inset-0 opacity-5">
          <div className="absolute top-1/4 left-1/4 w-64 h-64 border border-primary/20 rounded-full" />
          <div className="absolute bottom-1/4 right-1/4 w-48 h-48 border border-primary/20 rounded-full" />
          <div className="absolute top-1/2 right-1/3 w-32 h-32 border border-primary/20 rotate-45" />
        </div>
        
        <div className="relative z-10 text-center max-w-4xl mx-auto">
          <div className="inline-flex items-center gap-2 mb-6 px-4 py-2 rounded-full bg-primary/10 text-primary text-sm font-medium">
            <Sword className="w-4 h-4" />
            <span>Go 道場</span>
          </div>
          
          <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold mb-6 leading-tight">
            {t('onboarding.hero.title')}
          </h1>
          
          <p className="text-lg md:text-xl text-muted-foreground mb-8 max-w-2xl mx-auto leading-relaxed">
            {t('onboarding.hero.subtitle')}
          </p>
          
          <Link href="/">
            <Button size="lg" className="text-lg px-8 py-6" data-testid="button-hero-cta">
              {t('onboarding.hero.cta')}
              <ChevronRight className="ml-2 h-5 w-5" />
            </Button>
          </Link>
        </div>
      </section>

      <section className="py-20 px-4 bg-card/50">
        <div className="container max-w-6xl mx-auto">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div>
              <div className="inline-flex items-center gap-2 mb-4 text-primary">
                <Target className="w-5 h-5" />
                <span className="text-sm font-medium uppercase tracking-wide">Философия</span>
              </div>
              <h2 className="text-3xl md:text-4xl font-bold mb-6">
                {t('onboarding.philosophy.title')}
              </h2>
              <p className="text-lg text-muted-foreground leading-relaxed">
                {t('onboarding.philosophy.description')}
              </p>
            </div>
            
            <div className="relative">
              <div className="aspect-square max-w-md mx-auto relative">
                <div className="absolute inset-0 bg-gradient-to-br from-primary/20 to-primary/5 rounded-full" />
                <div className="absolute inset-8 border-2 border-primary/20 rounded-full" />
                <div className="absolute inset-16 border border-primary/30 rounded-full" />
                <div className="absolute inset-0 flex items-center justify-center">
                  <span className="text-8xl font-bold text-primary/20" style={{ fontFamily: "'Noto Sans JP', sans-serif" }}>
                    道
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="py-20 px-4">
        <div className="container max-w-6xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              {t('onboarding.skills.title')}
            </h2>
          </div>
          
          <div className="grid md:grid-cols-3 gap-6">
            {skills.map((skill, index) => (
              <Card key={index} className="hover-elevate group">
                <CardContent className="p-6">
                  <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4 group-hover:bg-primary/20 transition-colors">
                    <skill.icon className="w-6 h-6 text-primary" />
                  </div>
                  <h3 className="text-xl font-semibold mb-2">{skill.title}</h3>
                  <p className="text-muted-foreground">{skill.description}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      <section className="py-20 px-4 bg-card/50">
        <div className="container max-w-4xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 mb-4 text-primary">
            <Shield className="w-5 h-5" />
            <span className="text-sm font-medium uppercase tracking-wide">Подход</span>
          </div>
          <h2 className="text-3xl md:text-4xl font-bold mb-6">
            {t('onboarding.approach.title')}
          </h2>
          <p className="text-lg text-muted-foreground leading-relaxed max-w-3xl mx-auto">
            {t('onboarding.approach.description')}
          </p>
        </div>
      </section>

      <section className="py-20 px-4">
        <div className="container max-w-6xl mx-auto">
          <h2 className="text-3xl md:text-4xl font-bold mb-12 text-center">
            {t('onboarding.path.title')}
          </h2>
          
          <div className="relative">
            <div className="hidden md:block absolute top-1/2 left-0 right-0 h-0.5 bg-border -translate-y-1/2" />
            
            <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
              {pathSteps.map((step, index) => (
                <div key={index} className="relative text-center">
                  <div className="w-12 h-12 mx-auto mb-3 rounded-full bg-primary text-primary-foreground flex items-center justify-center font-bold text-lg relative z-10">
                    {index + 1}
                  </div>
                  <p className="text-sm font-medium">{step.title}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section className="py-20 px-4 bg-primary text-primary-foreground">
        <div className="container max-w-4xl mx-auto text-center">
          <h2 className="text-3xl md:text-4xl font-bold mb-4">
            {t('onboarding.cta.title')}
          </h2>
          <p className="text-lg opacity-90 mb-8">
            {t('onboarding.cta.description')}
          </p>
          <Link href="/">
            <Button size="lg" variant="secondary" className="text-lg px-8" data-testid="button-cta-bottom">
              {t('onboarding.cta.button')}
              <ChevronRight className="ml-2 h-5 w-5" />
            </Button>
          </Link>
        </div>
      </section>

      <footer className="py-8 px-4 border-t border-border">
        <div className="container max-w-6xl mx-auto text-center text-muted-foreground text-sm">
          {t('footer.copyright')}
        </div>
      </footer>
    </div>
  );
}
