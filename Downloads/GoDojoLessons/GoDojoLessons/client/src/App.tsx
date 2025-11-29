import { Switch, Route } from "wouter";
import { queryClient } from "./lib/queryClient";
import { QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "@/components/ui/toaster";
import { TooltipProvider } from "@/components/ui/tooltip";
import { ThemeProvider } from "@/lib/theme";
import { Header } from "@/components/Header";
import Onboarding from "@/pages/Onboarding";
import Topics from "@/pages/Topics";
import TopicDetail from "@/pages/TopicDetail";
import LessonPage from "@/pages/Lesson";
import Blog from "@/pages/Blog";
import BlogPost from "@/pages/BlogPost";
import AdminPanel from "@/pages/AdminPanel";
import NotFound from "@/pages/not-found";
import "@/lib/i18n";

function Router() {
  return (
    <Switch>
      <Route path="/" component={Topics} />
      <Route path="/onboarding" component={Onboarding} />
      <Route path="/topic/:id" component={TopicDetail} />
      <Route path="/lesson/:id" component={LessonPage} />
      <Route path="/blog" component={Blog} />
      <Route path="/blog/:id" component={BlogPost} />
      <Route path="/adminpanelka" component={AdminPanel} />
      <Route component={NotFound} />
    </Switch>
  );
}

function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-background">
      <Header />
      <main>{children}</main>
    </div>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <TooltipProvider>
          <AppLayout>
            <Router />
          </AppLayout>
          <Toaster />
        </TooltipProvider>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;
