/**
 * FlowMason Studio App
 *
 * Main application component with routing and theme support.
 */

import { useState } from 'react';
import { Routes, Route, NavLink, Navigate } from 'react-router-dom';
import { GitBranch, Package, Settings, Sun, Moon, Monitor, FileText, Terminal, BookTemplate, Activity, MessageSquare, Shield, Wand2, Briefcase } from 'lucide-react';
import { PipelinesPage } from './pages/PipelinesPage';
import { PipelineBuilderEnhanced } from './pages/PipelineBuilderEnhanced';
import { PackagesPage } from './pages/PackagesPage';
import { SettingsPage } from './pages/SettingsPage';
import { LogsPage } from './pages/LogsPage';
import { TemplatesPage } from './pages/TemplatesPage';
import { OperationsPage } from './pages/OperationsPage';
import { ApiConsolePage } from './pages/ApiConsolePage';
import { AdminPage } from './pages/AdminPage';
import { GeneratePage } from './pages/GeneratePage';
import { SolutionsPage } from './pages/SolutionsPage';
import { LogsPanel } from './components/LogsPanel';
import { ThemeProvider, useTheme } from './hooks/useTheme';
import { Tooltip, TooltipContent, TooltipProvider, TooltipTrigger } from '@/components/ui';

function ThemeToggleButton() {
  const { theme, resolvedTheme, setTheme } = useTheme();

  const cycleTheme = () => {
    if (theme === 'light') {
      setTheme('dark');
    } else if (theme === 'dark') {
      setTheme('system');
    } else {
      setTheme('light');
    }
  };

  const getIcon = () => {
    if (theme === 'system') {
      return <Monitor className="w-5 h-5" />;
    }
    return resolvedTheme === 'dark' ? (
      <Moon className="w-5 h-5" />
    ) : (
      <Sun className="w-5 h-5" />
    );
  };

  const getLabel = () => {
    if (theme === 'system') return 'System theme';
    return theme === 'dark' ? 'Dark theme' : 'Light theme';
  };

  return (
    <Tooltip>
      <TooltipTrigger asChild>
        <button
          onClick={cycleTheme}
          className="w-12 h-12 rounded-lg flex items-center justify-center text-gray-400 hover:text-white hover:bg-gray-800 transition-colors"
        >
          {getIcon()}
        </button>
      </TooltipTrigger>
      <TooltipContent side="right">
        {getLabel()}
      </TooltipContent>
    </Tooltip>
  );
}

function DevConsoleButton({ isOpen, onClick }: { isOpen: boolean; onClick: () => void }) {
  return (
    <Tooltip>
      <TooltipTrigger asChild>
        <button
          onClick={onClick}
          className={`w-12 h-12 rounded-lg flex items-center justify-center transition-colors ${
            isOpen
              ? 'bg-primary-600 text-white shadow-md'
              : 'text-gray-400 hover:text-white hover:bg-gray-800'
          }`}
        >
          <Terminal className="w-5 h-5" />
        </button>
      </TooltipTrigger>
      <TooltipContent side="right">
        Developer Console
      </TooltipContent>
    </Tooltip>
  );
}

function AppContent() {
  const [logsPanelOpen, setLogsPanelOpen] = useState(false);

  return (
    <div className="min-h-screen bg-background text-foreground">
      <div className="flex h-screen">
        {/* Sidebar navigation - always visible */}
        <nav className="w-16 bg-gray-900 dark:bg-gray-950 flex flex-col items-center py-4 flex-shrink-0">
          <div className="mb-8">
            <div className="w-10 h-10 bg-primary-600 rounded-lg flex items-center justify-center shadow-lg">
              <span className="text-white font-bold text-lg">F</span>
            </div>
          </div>

          <NavItem to="/pipelines" icon={<GitBranch />} label="Pipelines" />
          <NavItem to="/generate" icon={<Wand2 />} label="AI Generate" />
          <NavItem to="/operations" icon={<Activity />} label="Operations" />
          <NavItem to="/console" icon={<MessageSquare />} label="API Console" />
          <NavItem to="/admin" icon={<Shield />} label="Admin" />
          <NavItem to="/templates" icon={<BookTemplate />} label="Templates" />
          <NavItem to="/solutions" icon={<Briefcase />} label="Solutions" />
          <NavItem to="/packages" icon={<Package />} label="Packages" />
          <NavItem to="/logs" icon={<FileText />} label="Logs" />
          <NavItem to="/settings" icon={<Settings />} label="Settings" />

          {/* Developer Console toggle */}
          <div className="mt-auto mb-2">
            <DevConsoleButton
              isOpen={logsPanelOpen}
              onClick={() => setLogsPanelOpen(!logsPanelOpen)}
            />
          </div>

          {/* Theme toggle */}
          <ThemeToggleButton />
        </nav>

        {/* Main content */}
        <div className="flex-1 overflow-auto">
          <Routes>
            <Route path="/" element={<Navigate to="/pipelines" replace />} />
            <Route path="/pipelines" element={<PipelinesPage />} />
            <Route path="/pipelines/:id" element={<PipelineBuilderEnhanced />} />
            <Route path="/generate" element={<GeneratePage />} />
            <Route path="/operations" element={<OperationsPage />} />
            <Route path="/console" element={<ApiConsolePage />} />
            <Route path="/admin" element={<AdminPage />} />
            <Route path="/templates" element={<TemplatesPage />} />
            <Route path="/solutions" element={<SolutionsPage />} />
            <Route path="/packages" element={<PackagesPage />} />
            <Route path="/logs" element={<LogsPage />} />
            <Route path="/settings" element={<SettingsPage />} />
          </Routes>
        </div>

        {/* Floating logs panel */}
        <LogsPanel isOpen={logsPanelOpen} onClose={() => setLogsPanelOpen(false)} />
      </div>
    </div>
  );
}

function App() {
  return (
    <ThemeProvider>
      <TooltipProvider>
        <AppContent />
      </TooltipProvider>
    </ThemeProvider>
  );
}

interface NavItemProps {
  to: string;
  icon: React.ReactNode;
  label: string;
}

function NavItem({ to, icon, label }: NavItemProps) {
  return (
    <Tooltip>
      <TooltipTrigger asChild>
        <NavLink
          to={to}
          className={({ isActive }) =>
            `w-12 h-12 rounded-lg flex items-center justify-center mb-2 transition-colors ${
              isActive
                ? 'bg-primary-600 text-white shadow-md'
                : 'text-gray-400 hover:text-white hover:bg-gray-800'
            }`
          }
        >
          <div className="w-5 h-5">{icon}</div>
        </NavLink>
      </TooltipTrigger>
      <TooltipContent side="right">
        {label}
      </TooltipContent>
    </Tooltip>
  );
}

export default App;
