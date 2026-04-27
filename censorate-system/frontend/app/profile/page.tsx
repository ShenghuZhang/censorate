'use client';

import { useState, useEffect } from 'react';
import {
  Save,
  Edit,
  Star,
  MoreHorizontal,
  CheckCircle2,
  MessageSquare,
  Settings,
  FolderKanban,
  Terminal,
  Shield,
  Clock
} from 'lucide-react';
import { useAuth } from '@/app/hooks/useAuth';
import { useRouter } from 'next/navigation';
import Layout from '@/app/components/layout/Layout';
import { profileAPI, UserProject, UserActivity, ContributionHeatmap } from '@/lib/api/profile';

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
  const { user, logout } = useAuth();
  const router = useRouter();
  const userAlias = user?.name || (user?.email ? user.email.split('@')[0] : 'User');
  const [activeTab, setActiveTab] = useState('overview');
  const [loading, setLoading] = useState(true);
  const [projects, setProjects] = useState<UserProject[]>([]);
  const [activities, setActivities] = useState<UserActivity[]>([]);
  const [heatmap, setHeatmap] = useState<ContributionHeatmap | null>(null);

  // Language colors for display
  const languageColors: { [key: string]: string } = {
    'TypeScript': '#3178c6',
    'JavaScript': '#f1e05a',
    'Python': '#3572A5',
    'Go': '#00add8',
    'Rust': '#dea584',
    'default': '#6e7681'
  };

  // Icon mapping
  const iconMapping = [Settings, FolderKanban, Terminal, Shield];

  useEffect(() => {
    async function loadProfileData() {
      if (!user?.id) return;

      try {
        setLoading(true);
        const [userProjects, userActivities, userHeatmap] = await Promise.all([
          profileAPI.getUserProjects(user.id).catch(e => { console.log('Projects fetch failed'); return []; }),
          profileAPI.getUserActivity(user.id).catch(e => { console.log('Activity fetch failed'); return []; }),
          profileAPI.getUserHeatmap(user.id).catch(e => { console.log('Heatmap fetch failed'); return null; })
        ]);
        setProjects(userProjects);
        setActivities(userActivities);
        setHeatmap(userHeatmap);
      } catch (error) {
        console.error('Failed to load profile data:', error);
      } finally {
        setLoading(false);
      }
    }

    loadProfileData();
  }, [user?.id]);


  const formatTimeAgo = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffMins < 1) return 'just now';
    if (diffMins < 60) return `${diffMins} minutes ago`;
    if (diffHours < 24) return `${diffHours} hours ago`;
    if (diffDays < 7) return `${diffDays} days ago`;
    return date.toLocaleDateString();
  };

  const getActivityIcon = (type: string) => {
    switch (type) {
      case 'comment': return MessageSquare;
      case 'status_change': return CheckCircle2;
      default: return Edit;
    }
  };

  // Generate heatmap grid (52 weeks x 7 days)
  const generateHeatmapGrid = () => {
    if (!heatmap) return null;

    const dateMap = new Map<string, number>();
    heatmap.contributions.forEach(c => dateMap.set(c.date, c.count));

    // Calculate max count for shading
    const maxCount = Math.max(...heatmap.contributions.map(c => c.count), 1);

    const grid = [];
    const today = new Date();

    for (let weekIdx = 0; weekIdx < 52; weekIdx++) {
      const week = [];
      for (let dayIdx = 0; dayIdx < 7; dayIdx++) {
        const date = new Date(today);
        date.setDate(date.getDate() - ((51 - weekIdx) * 7 + (6 - dayIdx)));
        const dateStr = date.toISOString().split('T')[0];
        const count = dateMap.get(dateStr) || 0;

        let colorClass = 'bg-slate-100';
        if (count > 0) {
          const ratio = Math.min(count / maxCount, 1);
          if (ratio > 0.75) colorClass = 'bg-green-800';
          else if (ratio > 0.5) colorClass = 'bg-green-600';
          else if (ratio > 0.25) colorClass = 'bg-green-400';
          else colorClass = 'bg-green-200';
        }

        week.push({ date: dateStr, count, colorClass });
      }
      grid.push(week);
    }

    return grid;
  };

  const heatmapGrid = generateHeatmapGrid();

  return (
    <Layout>
      <div className="max-w-7xl mx-auto pt-8 pb-16 px-4">
        <div className="flex flex-col lg:flex-row gap-12">
          {/* Left Sidebar */}
          <aside className="w-full lg:w-80 flex-shrink-0">
            <div className="relative group mb-8">
              <div className="w-48 h-48 rounded-2xl overflow-hidden bg-gradient-to-br from-gray-400 to-gray-600 flex items-center justify-center text-white text-6xl font-bold shadow-md mx-auto lg:mx-0">
                {userAlias.charAt(0).toUpperCase()}
              </div>
            </div>
            <div className="space-y-1 mb-6 text-center lg:text-left">
              <h1 className="text-3xl font-bold text-gray-900 tracking-tight">{userAlias}</h1>
              <p className="text-lg text-gray-500 font-medium">{user?.email}</p>
              <p className="text-sm text-gray-500">Product Engineer</p>
            </div>
            <p className="text-gray-600 text-sm leading-relaxed mb-6 text-center lg:text-left">
              Product Engineer. Focused on building AI-native requirement management systems and scalable architecture.
            </p>
          </aside>

          {/* Main Content */}
          <div className="flex-1">
            {/* Navigation Tabs */}
            <nav className="flex items-center gap-8 mb-8 border-b border-gray-200">
              <button
                onClick={() => setActiveTab('overview')}
                className={`pb-4 border-b-2 text-gray-900 font-semibold flex items-center gap-2 transition-colors ${
                  activeTab === 'overview'
                    ? 'border-blue-600'
                    : 'border-transparent text-gray-400 hover:text-gray-600'
                }`}
              >
                <span className="text-[18px]">📋</span>
                Overview
              </button>
            </nav>

            {loading ? (
              <div className="flex items-center justify-center py-12">
                <div className="flex items-center gap-3 text-gray-500">
                  <div className="w-6 h-6 border-2 border-gray-200 border-t-gray-600 rounded-full animate-spin"></div>
                  <span>Loading...</span>
                </div>
              </div>
            ) : (
              <>
                {/* Pinned Projects Section */}
                <section className="mb-12">
                  <div className="flex items-center justify-between mb-6">
                    <h2 className="text-sm font-bold text-gray-400 uppercase tracking-widest">Pinned Projects</h2>
                    <button className="text-xs font-semibold text-blue-600 hover:underline transition-all">
                      Customize pins
                    </button>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {projects.length > 0 ? projects.map((project, idx) => {
                      const Icon = iconMapping[idx % iconMapping.length];
                      const langColor = languageColors['TypeScript'];
                      return (
                        <div
                          key={project.id}
                          className="bg-white p-5 rounded-2xl border border-gray-200 transition-all hover:shadow-md group"
                        >
                          <div className="flex items-start justify-between mb-4">
                            <div className="flex items-center gap-2">
                              <Icon size={20} className="text-blue-600" />
                              <h3 className="font-bold text-blue-600 group-hover:underline cursor-pointer">
                                {project.name}
                              </h3>
                            </div>
                            <span className="text-[10px] font-bold px-2 py-0.5 rounded-full border border-gray-200 text-gray-400 uppercase tracking-tighter">
                              Internal
                            </span>
                          </div>
                          <p className="text-sm text-gray-600 mb-6 line-clamp-2">
                            {project.description || 'No description available'}
                          </p>
                          <div className="flex items-center gap-4">
                            <div className="flex items-center gap-1.5">
                              <span className="w-3 h-3 rounded-full" style={{ backgroundColor: langColor }}></span>
                              <span className="text-xs text-gray-400">TypeScript</span>
                            </div>
                            <div className="flex items-center gap-1 text-gray-400">
                              <Star size={14} fill="currentColor" />
                              <span className="text-xs">0</span>
                            </div>
                          </div>
                        </div>
                      );
                    }) : (
                      <div className="col-span-2 text-center py-12 text-gray-400">
                        <p>No projects yet</p>
                        <p className="text-sm mt-2">Join a project to see it here</p>
                      </div>
                    )}
                  </div>
                </section>

                {/* Contribution Heatmap */}
                <section className="mb-12">
                  <h2 className="text-sm font-bold text-gray-400 uppercase tracking-widest mb-6">
                    {heatmap ? `${heatmap.total} contributions in the last year` : '0 contributions in the last year'}
                  </h2>
                  <div className="bg-white p-6 rounded-2xl border border-gray-200 shadow-sm">
                    <div className="flex gap-2">
                      {/* Weekday labels */}
                      <div className="flex flex-col justify-around text-xs text-gray-400 w-10 pr-2 pt-6">
                        <span>Mon</span>
                        <span>Wed</span>
                        <span>Fri</span>
                      </div>

                      {/* Heatmap grid */}
                      <div className="flex-1">
                        {/* Month labels */}
                        <div className="flex justify-between text-xs text-gray-400 mb-2 px-1">
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
                          {heatmapGrid ? heatmapGrid.map((week, weekIdx) => (
                            <div key={weekIdx} className="flex flex-col gap-1">
                              {week.map((day, dayIdx) => (
                                <div
                                  key={dayIdx}
                                  className={`w-2.5 h-2.5 rounded-sm ${day.colorClass} border border-slate-200`}
                                  title={`${day.count} contributions on ${day.date}`}
                                ></div>
                              ))}
                            </div>
                          )) : Array.from({ length: 52 }).map((_, weekIdx) => (
                            <div key={weekIdx} className="flex flex-col gap-1">
                              {Array.from({ length: 7 }).map((_, dayIdx) => (
                                <div
                                  key={dayIdx}
                                  className="w-2.5 h-2.5 rounded-sm bg-slate-100 border border-slate-200"
                                ></div>
                              ))}
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>

                    {/* Legend */}
                    <div className="flex items-center justify-between mt-4">
                      <a href="#" className="text-sm text-gray-500 hover:text-blue-600 transition-colors">
                        Learn how we count contributions
                      </a>
                      <div className="flex items-center gap-2 text-sm text-gray-400">
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
                  <h2 className="text-sm font-bold text-gray-400 uppercase tracking-widest mb-6">
                    Recent Activity
                  </h2>
                  <div className="space-y-0 relative before:absolute before:left-[11px] before:top-2 before:bottom-2 before:w-[1px] before:bg-gray-200">
                    {activities.length > 0 ? activities.map((activity, index) => {
                      const Icon = getActivityIcon(activity.type);
                      return (
                        <div
                          key={activity.id}
                          className="relative pl-10 py-4 group"
                        >
                          <div className="absolute left-0 top-[22px] w-[24px] h-[24px] bg-white border border-gray-200 rounded-full flex items-center justify-center z-10">
                            <Icon size={14} className="text-blue-600 fill-blue-600" />
                          </div>
                          <div className="flex items-center gap-2 text-sm text-gray-900">
                            <span className="font-semibold">{activity.action}</span>
                            <span className="font-semibold text-blue-600 cursor-pointer hover:underline">
                              {activity.target}
                            </span>
                            {activity.note && index === 0 && (
                              <span className="text-gray-900">: {activity.note}</span>
                            )}
                            <span className="text-xs text-gray-400 ml-2">{formatTimeAgo(activity.timestamp)}</span>
                          </div>
                        </div>
                      );
                    }) : (
                      <div className="text-center py-12 text-gray-400">
                        <p>No recent activity</p>
                        <p className="text-sm mt-2">Activity will appear here when you start contributing</p>
                      </div>
                    )}
                  </div>
                  <button className="w-full mt-8 py-3 rounded-2xl border border-gray-200 text-sm font-semibold text-gray-400 hover:bg-gray-50 transition-colors">
                    View older activity
                  </button>
                </section>
              </>
            )}
          </div>
        </div>
      </div>
    </Layout>
  );
}
