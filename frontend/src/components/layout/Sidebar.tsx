import React, { useEffect, useState } from 'react';
import { NavLink, useNavigate, useLocation } from 'react-router-dom';
import { 
  Plus, MessageSquare, Bookmark, Scale, Settings, Database, 
  LogOut, Sparkles, Car, Trash2, Search, ChevronLeft, ChevronRight
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { getConversations, deleteConversation } from '../../api/chat';
import { Conversation } from '../../types/chat';

interface SidebarProps {
  onNewChat?: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ onNewChat }) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [collapsed, setCollapsed] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  const loadConversations = async () => {
    try {
      const list = await getConversations();
      setConversations(list);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    if (user) {
      loadConversations();
    }
  }, [user, location.pathname, location.search]);

  const handleDelete = async (e: React.MouseEvent, id: number) => {
    e.preventDefault();
    e.stopPropagation();
    try {
      await deleteConversation(id);
      setConversations((prev) => prev.filter((c) => c.id !== id));
      if (location.pathname.includes(`/chat/${id}`)) {
        navigate('/app');
      }
    } catch (e) {
      console.error(e);
    }
  };

  const filteredConversations = conversations.filter((c) =>
    c.title.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <aside
      className={`relative flex flex-col justify-between h-screen transition-all duration-300 z-30 ${
        collapsed ? 'w-20' : 'w-64'
      }`}
      style={{
        background: '#EFECE5',
        borderRight: '1px solid #E2DDD6',
        color: '#0D0D0D'
      }}
    >
      {/* Collapse Toggle Button */}
      <button
        onClick={() => setCollapsed(!collapsed)}
        className="absolute -right-3.5 top-7 p-1.5 rounded-full shadow-sm z-40 transition-colors"
        style={{ background: '#FFFFFF', border: '1px solid #E2DDD6', color: '#6B6560' }}
      >
        {collapsed ? <ChevronRight className="w-3.5 h-3.5" /> : <ChevronLeft className="w-3.5 h-3.5" />}
      </button>

      {/* Top Header & Logo */}
      <div>
        <div className="p-4 flex items-center gap-3" style={{ borderBottom: '1px solid #E2DDD6' }}>
          <div className="p-2 rounded-xl text-white shrink-0 shadow-sm" style={{ background: '#C96A2B' }}>
            <Car className="w-5 h-5" />
          </div>
          {!collapsed && (
            <div>
              <h1 className="text-base font-bold tracking-tight flex items-center gap-1.5" style={{ color: '#0D0D0D' }}>
                AutoMind <span className="font-mono text-xs px-1.5 py-0.5 rounded" style={{ background: '#F7F4ED', border: '1px solid #E2DDD6', color: '#C96A2B' }}>AI</span>
              </h1>
              <p className="text-[10px]" style={{ color: '#6B6560' }}>Car Research Intelligence</p>
            </div>
          )}
        </div>

        {/* New Chat Button */}
        <div className="p-3">
          <button
            onClick={() => {
              if (onNewChat) onNewChat();
              navigate('/app');
            }}
            className={`w-full flex items-center gap-2.5 px-3.5 py-2.5 rounded-xl font-medium text-sm transition-all cursor-pointer shadow-sm ${
              collapsed ? 'justify-center px-0' : ''
            }`}
            style={{ background: '#C96A2B', color: '#FFFFFF' }}
          >
            <Plus className="w-4 h-4 shrink-0" />
            {!collapsed && <span>New Car Research</span>}
          </button>
        </div>

        {/* Search Input for Chats */}
        {!collapsed && (
          <div className="px-3 mb-2">
            <div className="relative">
              <Search className="w-3.5 h-3.5 absolute left-3 top-2.5" style={{ color: '#9C9590' }} />
              <input
                type="text"
                placeholder="Search chats..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full rounded-lg pl-8 pr-3 py-1.5 text-xs outline-none"
                style={{ background: '#FFFFFF', border: '1px solid #E2DDD6', color: '#0D0D0D' }}
              />
            </div>
          </div>
        )}

        {/* Main Nav Section */}
        <div className="px-3 space-y-1">
          <NavLink
            to="/app"
            end
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2 rounded-xl text-xs font-medium transition-all ${
                isActive
                  ? 'font-semibold shadow-sm'
                  : 'hover:bg-white/60'
              }`
            }
            style={({ isActive }) => ({
              background: isActive ? '#FFFFFF' : 'transparent',
              color: isActive ? '#C96A2B' : '#4A4540',
              border: isActive ? '1px solid #E2DDD6' : '1px solid transparent'
            })}
          >
            <Sparkles className="w-4 h-4 shrink-0" />
            {!collapsed && <span>Research Hub</span>}
          </NavLink>

          <NavLink
            to="/saved"
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2 rounded-xl text-xs font-medium transition-all ${
                isActive ? 'font-semibold shadow-sm' : 'hover:bg-white/60'
              }`
            }
            style={({ isActive }) => ({
              background: isActive ? '#FFFFFF' : 'transparent',
              color: isActive ? '#C96A2B' : '#4A4540',
              border: isActive ? '1px solid #E2DDD6' : '1px solid transparent'
            })}
          >
            <Bookmark className="w-4 h-4 shrink-0" />
            {!collapsed && <span>Saved Vehicles</span>}
          </NavLink>

          <NavLink
            to="/compare"
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2 rounded-xl text-xs font-medium transition-all ${
                isActive ? 'font-semibold shadow-sm' : 'hover:bg-white/60'
              }`
            }
            style={({ isActive }) => ({
              background: isActive ? '#FFFFFF' : 'transparent',
              color: isActive ? '#C96A2B' : '#4A4540',
              border: isActive ? '1px solid #E2DDD6' : '1px solid transparent'
            })}
          >
            <Scale className="w-4 h-4 shrink-0" />
            {!collapsed && <span>Compare Models</span>}
          </NavLink>
        </div>

        {/* Recent Conversations List */}
        {!collapsed && (
          <div className="mt-4 px-3">
            <div className="text-[10px] font-bold uppercase tracking-wider px-2 mb-1" style={{ color: '#9C9590' }}>
              Recent Conversations
            </div>
            <div className="max-h-48 overflow-y-auto space-y-0.5 pr-1">
              {filteredConversations.length === 0 ? (
                <p className="text-[11px] px-2 py-1" style={{ color: '#9C9590' }}>No chats found.</p>
              ) : (
                filteredConversations.map((c) => (
                  <NavLink
                    key={c.id}
                    to={`/app?conv=${c.id}`}
                    className={({ isActive }) =>
                      `group flex items-center justify-between px-2.5 py-1.5 rounded-lg text-xs transition-all ${
                        isActive ? 'font-medium shadow-sm' : 'hover:bg-white/50'
                      }`
                    }
                    style={({ isActive }) => ({
                      background: isActive ? '#FFFFFF' : 'transparent',
                      color: isActive ? '#0D0D0D' : '#6B6560',
                      border: isActive ? '1px solid #E2DDD6' : '1px solid transparent'
                    })}
                  >
                    <div className="flex items-center gap-2 truncate">
                      <MessageSquare className="w-3.5 h-3.5 shrink-0 opacity-70" />
                      <span className="truncate">{c.title}</span>
                    </div>
                    <button
                      onClick={(e) => handleDelete(e, c.id)}
                      className="opacity-0 group-hover:opacity-100 p-1 hover:text-red-600 transition-opacity"
                    >
                      <Trash2 className="w-3 h-3" />
                    </button>
                  </NavLink>
                ))
              )}
            </div>
          </div>
        )}
      </div>

      {/* Footer User Profile & Controls */}
      <div className="p-3 space-y-1" style={{ borderTop: '1px solid #E2DDD6' }}>
        {user?.is_admin && (
          <NavLink
            to="/admin/data"
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2 rounded-xl text-xs font-medium transition-all ${
                isActive ? 'font-semibold shadow-sm' : 'hover:bg-white/60'
              }`
            }
            style={({ isActive }) => ({
              background: isActive ? '#FFFFFF' : 'transparent',
              color: isActive ? '#C96A2B' : '#4A4540',
              border: isActive ? '1px solid #E2DDD6' : '1px solid transparent'
            })}
          >
            <Database className="w-4 h-4 shrink-0" style={{ color: '#C96A2B' }} />
            {!collapsed && <span>Admin Ingestion</span>}
          </NavLink>
        )}

        <NavLink
          to="/settings"
          className={({ isActive }) =>
            `flex items-center gap-3 px-3 py-2 rounded-xl text-xs font-medium transition-all ${
              isActive ? 'font-semibold shadow-sm' : 'hover:bg-white/60'
            }`
          }
          style={({ isActive }) => ({
            background: isActive ? '#FFFFFF' : 'transparent',
            color: isActive ? '#C96A2B' : '#4A4540',
            border: isActive ? '1px solid #E2DDD6' : '1px solid transparent'
          })}
        >
          <Settings className="w-4 h-4 shrink-0" />
          {!collapsed && <span>Settings</span>}
        </NavLink>

        <div className="pt-2 flex items-center justify-between" style={{ borderTop: '1px solid #E2DDD6' }}>
          <div className="flex items-center gap-2.5 truncate">
            <div className="w-8 h-8 rounded-full flex items-center justify-center text-white text-xs font-bold shrink-0" style={{ background: '#0D0D0D' }}>
              {user?.full_name?.charAt(0) || 'U'}
            </div>
            {!collapsed && (
              <div className="truncate">
                <p className="text-xs font-semibold truncate" style={{ color: '#0D0D0D' }}>{user?.full_name}</p>
                <p className="text-[10px] truncate" style={{ color: '#6B6560' }}>{user?.email}</p>
              </div>
            )}
          </div>

          {!collapsed && (
            <button
              onClick={logout}
              className="p-1.5 rounded-lg transition-colors hover:bg-red-50 hover:text-red-600"
              style={{ color: '#6B6560' }}
              title="Logout"
            >
              <LogOut className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>
    </aside>
  );
};
