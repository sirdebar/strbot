import { useTranslation } from 'react-i18next';
import { Link, useLocation } from 'wouter';
import { Moon, Sun, Globe, Menu, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { useTheme } from '@/lib/theme';
import { useState } from 'react';

export function Header() {
  const { t, i18n } = useTranslation();
  const { theme, toggleTheme } = useTheme();
  const [location] = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const changeLanguage = (lng: string) => {
    i18n.changeLanguage(lng);
    localStorage.setItem('language', lng);
  };

  const navLinks = [
    { href: '/', label: t('nav.topics') },
    { href: '/blog', label: t('nav.blog') },
    { href: '/onboarding', label: t('nav.onboarding') },
  ];

  return (
    <header className="sticky top-0 z-50 w-full border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="flex h-16 items-center px-4 md:px-6">
        <Link href="/" className="flex items-center gap-2 group flex-shrink-0" data-testid="link-logo">
          <span className="text-xl font-bold text-primary tracking-tight">
            GO-DOJO
          </span>
          <span className="text-muted-foreground">|</span>
          <span className="text-lg font-medium text-foreground" style={{ fontFamily: "'Noto Sans JP', sans-serif" }}>
            ご 道場
          </span>
        </Link>

        <nav className="hidden md:flex flex-1 items-center justify-center gap-6">
          {navLinks.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className={`text-sm font-medium transition-colors ${
                location === link.href
                  ? 'text-primary'
                  : 'text-muted-foreground hover:text-foreground'
              }`}
              data-testid={`link-nav-${link.href.replace('/', '') || 'home'}`}
            >
              {link.label}
            </Link>
          ))}
        </nav>

        <div className="flex items-center gap-2 ml-auto">
          <Button
            variant="ghost"
            size="icon"
            onClick={toggleTheme}
            aria-label={theme === 'light' ? t('theme.dark') : t('theme.light')}
            data-testid="button-theme-toggle"
          >
            {theme === 'light' ? (
              <Moon className="h-5 w-5" />
            ) : (
              <Sun className="h-5 w-5" />
            )}
          </Button>

          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="icon" data-testid="button-language-toggle">
                <Globe className="h-5 w-5" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end">
              <DropdownMenuItem
                onClick={() => changeLanguage('ru')}
                className={i18n.language === 'ru' ? 'bg-accent' : ''}
                data-testid="button-language-ru"
              >
                🇷🇺 {t('language.ru')}
              </DropdownMenuItem>
              <DropdownMenuItem
                onClick={() => changeLanguage('en')}
                className={i18n.language === 'en' ? 'bg-accent' : ''}
                data-testid="button-language-en"
              >
                🇬🇧 {t('language.en')}
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>

          <Button
            variant="ghost"
            size="icon"
            className="md:hidden"
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            data-testid="button-mobile-menu"
          >
            {mobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
          </Button>
        </div>
      </div>

      {mobileMenuOpen && (
        <nav className="md:hidden border-t border-border bg-background px-4 py-4">
          {navLinks.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              onClick={() => setMobileMenuOpen(false)}
              className={`block py-2 text-sm font-medium transition-colors ${
                location === link.href
                  ? 'text-primary'
                  : 'text-muted-foreground'
              }`}
              data-testid={`link-mobile-nav-${link.href.replace('/', '') || 'home'}`}
            >
              {link.label}
            </Link>
          ))}
        </nav>
      )}
    </header>
  );
}
