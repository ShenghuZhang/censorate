'use client';

import { useState } from 'react';
import { User, Mail, Save, Edit, Star, MoreHorizontal, Link, CheckCircle2, MessageSquare, Settings, FolderKanban, Terminal, Shield } from 'lucide-react';
import { useAuth } from '@/app/hooks/useAuth';
import Layout from '@/app/components/layout/Layout';

// Types
interface Project {
  id: string;
  name: string;
  description: string;
  language: string;
  languageColor: string;
  stars: number;
  visibility: 'Public' | 'Internal';
  icon: any;
}

interface Activity {
  id: string;
  type: 'review' | 'approve' | 'comment' | 'draft';
  text: string;
  target: string;
  time: string;
  icon: any;
}

export default function ProfilePage() {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('overview');
  const userAlias = user?.name || (user?.email ? user.email.split('@')[0] : 'User');

  // Mock data
  const projects: Project[] = [
    {
      id: '1',
      name: 'stratos-core-ui',
      description: 'The foundational design system and component library powering all Stratos enterprise applications.',
      language: 'TypeScript',
      languageColor: '#3178c6',
      stars: 1200,
      visibility: 'Public',
      icon: Settings
    },
    {
      id: '2',
      name: 'nexus-orchestrator',
      description: 'Multi-cloud deployment engine with automated resource allocation and real-time monitoring.',
      language: 'Go',
      languageColor: '#00add8',
      stars: 428,
      visibility: 'Internal',
      icon: FolderKanban
    },
    {
      id: '3',
      name: 'stratos-cli',
      description: 'Command-line interface for managing Stratos resources and local development environments.',
      language: 'JavaScript',
      languageColor: '#f1e05a',
      stars: 156,
      visibility: 'Public',
      icon: Terminal
    },
    {
      id: '4',
      name: 'auth-vault',
      description: 'High-security authentication layer implementing Zero-Trust principles for enterprise users.',
      language: 'Rust',
      languageColor: '#dea584',
      stars: 2100,
      visibility: 'Public',
      icon: Shield
    }
  ];

  const activities: Activity[] = [
    {
      id: '1',
      type: 'review',
      text: 'Reviewed',
      target: 'REQ-1024',
      time: '2 hours ago',
      icon: Edit
    },
    {
      id: '2',
      type: 'approve',
      text: 'Approved Design for',
      target: 'nexus-orchestrator',
      time: 'Yesterday',
      icon: CheckCircle2
    },
    {
      id: '3',
      type: 'comment',
      text: 'Commented on',
      target: 'REQ-992',
      time: '3 days ago',
      icon: MessageSquare
    },
    {
      id: '4',
      type: 'draft',
      text: 'Drafted Test Cases for',
      target: 'stratos-cli',
      time: 'Dec 12',
      icon: CheckCircle2
    }
  ];

  return (
    <Layout>
      <div className="max-w-7xl mx-auto pt-8 pb-16 animate-fade-in-up">
        <div className="flex flex-col lg:flex-row gap-12">
          {/* Left Sidebar */}
          <aside className="w-full lg:w-80 flex-shrink-0">
            <div className="relative group mb-8">
              <div className="w-48 h-48 rounded-2xl overflow-hidden bg-surface-soft border-4 border-surface shadow-soft mx-auto lg:mx-0">
                <div className="w-full h-full bg-gradient-to-br from-primary to-primary-dark flex items-center justify-center text-white text-6xl font-bold">
                  {userAlias.charAt(0).toUpperCase()}
                </div>
              </div>
            </div>
            <div className="space-y-1 mb-6 text-center lg:text-left">
              <h1 className="text-3xl font-bold text-text-primary tracking-tight">{userAlias}</h1>
              <p className="text-lg text-text-tertiary font-medium">{user?.email}</p>
              <p className="text-sm text-text-tertiary">Product Engineer</p>
            </div>
            <p className="text-text-secondary text-sm leading-relaxed mb-6 text-center lg:text-left">
              Product Engineer. Focused on building AI-native requirement management systems and scalable architecture.
            </p>
            <div className="flex items-center justify-center lg:justify-start gap-6 mb-8">
              <div className="flex items-center gap-1 text-sm">
                <span className="font-bold text-text-primary">1.4k</span>
                <span className="text-text-tertiary">followers</span>
              </div>
              <div className="flex items-center gap-1 text-sm">
                <span className="font-bold text-text-primary">842</span>
                <span className="text-text-tertiary">following</span>
              </div>
            </div>
            <div className="space-y-4 pt-6 border-t border-border">
              <div className="flex items-center justify-center lg:justify-start gap-3 text-sm text-text-secondary">
                <User size={20} className="text-text-muted" />
                <span>Censorate</span>
              </div>
              <div className="flex items-center justify-center lg:justify-start gap-3 text-sm text-text-secondary">
                <Mail size={20} className="text-text-muted" />
                <a href={`mailto:${user?.email}`} className="hover:text-primary transition-colors">
                  {user?.email}
                </a>
              </div>
              <div className="flex items-center justify-center lg:justify-start gap-3 text-sm text-text-secondary">
                <Link size={20} className="text-text-muted" />
                <a href="#" className="hover:text-primary transition-colors">censorate.io</a>
              </div>
            </div>
          </aside>

          {/* Main Content */}
          <div className="flex-1">
            {/* Navigation Tabs */}
            <nav className="flex items-center gap-8 mb-8 border-b border-border">
              <button
                onClick={() => setActiveTab('overview')}
                className={`pb-4 border-b-2 text-text-primary font-semibold flex items-center gap-2 transition-colors ${
                  activeTab === 'overview'
                    ? 'border-primary'
                    : 'border-transparent text-text-tertiary hover:text-text-secondary'
                }`}
              >
                <span className="text-[18px]">📋</span>
                Overview
              </button>
            </nav>

            {/* Pinned Projects Section */}
            <section className="mb-12">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-sm font-bold text-text-tertiary uppercase tracking-widest">Pinned Projects</h2>
                <button className="text-xs font-semibold text-primary hover:underline transition-all">
                  Customize pins
                </button>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {projects.map((project) => {
                  const Icon = project.icon;
                  return (
                    <div
                      key={project.id}
                      className="bg-surface p-5 rounded-2xl border border-border transition-all hover:shadow-medium hover:border-border-medium group"
                    >
                      <div className="flex items-start justify-between mb-4">
                        <div className="flex items-center gap-2">
                          <Icon size={20} className="text-primary" />
                          <h3 className="font-bold text-primary group-hover:underline cursor-pointer">
                            {project.name}
                          </h3>
                        </div>
                        <span className="text-[10px] font-bold px-2 py-0.5 rounded-full border border-border text-text-tertiary uppercase tracking-tighter">
                          {project.visibility}
                        </span>
                      </div>
                      <p className="text-sm text-text-secondary mb-6 line-clamp-2">
                        {project.description}
                      </p>
                      <div className="flex items-center gap-4">
                        <div className="flex items-center gap-1.5">
                          <span className="w-3 h-3 rounded-full" style={{ backgroundColor: project.languageColor }}></span>
                          <span className="text-xs text-text-tertiary">{project.language}</span>
                        </div>
                        <div className="flex items-center gap-1 text-text-tertiary">
                          <Star size={14} fill="currentColor" />
                          <span className="text-xs">{project.stars > 1000 ? `${(project.stars / 1000).toFixed(1)}k` : project.stars}</span>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </section>

            {/* Contribution Heatmap */}
            <section className="mb-12">
              <h2 className="text-sm font-bold text-text-tertiary uppercase tracking-widest mb-6">
                452 contributions in the last year
              </h2>
              <div className="bg-surface p-6 rounded-2xl border border-border shadow-soft">
                <div className="flex gap-2">
                  {/* Weekday labels */}
                  <div className="flex flex-col justify-around text-xs text-text-tertiary w-10 pr-2 pt-6">
                    <span>Mon</span>
                    <span>Wed</span>
                    <span>Fri</span>
                  </div>

                  {/* Heatmap grid */}
                  <div className="flex-1">
                    {/* Month labels */}
                    <div className="flex justify-between text-xs text-text-tertiary mb-2 px-1">
                      <span>Apr</span>
                      <span>May</span>
                      <span>Jun</span>
                      <span>Jul</span>
                      <span>Aug</span>
                      <span>Sep</span>
                      <span>Oct</span>
                      <span>Nov</span>
                      <span>Dec</span>
                      <span>Jan</span>
                      <span>Feb</span>
                      <span>Mar</span>
                      <span>Apr</span>
                    </div>

                    {/* Grid */}
                    <div className="flex gap-1">
                      {Array.from({ length: 52 }).map((_, weekIndex) => (
                        <div key={weekIndex} className="flex flex-col gap-1">
                          {Array.from({ length: 7 }).map((_, dayIndex) => {
                            const colorIndex = Math.floor(Math.random() * 5);
                            const shades = ['bg-slate-100', 'bg-green-200', 'bg-green-400', 'bg-green-600', 'bg-green-800'];
                            return (
                              <div
                                key={dayIndex}
                                className={`w-2.5 h-2.5 rounded-sm ${shades[colorIndex]} border border-slate-200`}
                              ></div>
                            );
                          })}
                        </div>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Legend */}
                <div className="flex items-center justify-between mt-4">
                  <a href="#" className="text-sm text-text-secondary hover:text-primary transition-colors">
                    Learn how we count contributions
                  </a>
                  <div className="flex items-center gap-2 text-sm text-text-tertiary">
                    <span>Less</span>
                    <div className="flex gap-1">
                      <div className="w-2.5 h-2.5 rounded-sm bg-slate-100 border border-slate-200"></div>
                      <div className="w-2.5 h-2.5 rounded-sm bg-green-200 border border-slate-200"></div>
                      <div className="w-2.5 h-2.5 rounded-sm bg-green-400 border border-slate-200"></div>
                      <div className="w-2.5 h-2.5 rounded-sm bg-green-600 border border-slate-200"></div>
                      <div className="w-2.5 h-2.5 rounded-sm bg-green-800 border border-slate-200"></div>
                    </div>
                    <span>More</span>
                  </div>
                </div>
              </div>
            </section>

            {/* Activity Feed */}
            <section>
              <h2 className="text-sm font-bold text-text-tertiary uppercase tracking-widest mb-6">
                Recent Activity
              </h2>
              <div className="space-y-0 relative before:absolute before:left-[11px] before:top-2 before:bottom-2 before:w-[1px] before:bg-border">
                {activities.map((activity, index) => {
                  const Icon = activity.icon;
                  return (
                    <div
                      key={activity.id}
                      className="relative pl-10 py-4 group"
                    >
                      <div className="absolute left-0 top-[22px] w-[24px] h-[24px] bg-surface border border-border rounded-full flex items-center justify-center z-10">
                        <Icon size={14} className="text-primary fill-primary" />
                      </div>
                      <div className="flex items-center gap-2 text-sm text-text-primary">
                        <span className="font-semibold">{activity.text}</span>
                        <span className="font-semibold text-primary cursor-pointer hover:underline">
                          {activity.target}
                        </span>
                        {index === 0 && <span className="text-text-primary">: API Authentication Layer</span>}
                        <span className="text-xs text-text-tertiary ml-2">{activity.time}</span>
                      </div>
                    </div>
                  );
                })}
              </div>
              <button className="w-full mt-8 py-3 rounded-2xl border border-border text-sm font-semibold text-text-tertiary hover:bg-surface-soft transition-colors">
                View older activity
              </button>
            </section>
          </div>
        </div>
      </div>
    </Layout>
  );
}
