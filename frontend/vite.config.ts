import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'
import fs from 'fs'

const backendTarget = process.env.VITE_BACKEND_URL || 'http://localhost:8000';

function spaFallbackPlugin() {
  return {
    name: 'spa-fallback-generator',
    closeBundle() {
      const distDir = path.resolve(__dirname, './dist');
      const indexPath = path.join(distDir, 'index.html');
      if (fs.existsSync(indexPath)) {
        // 1. Create 404.html for static hosting fallback
        fs.copyFileSync(indexPath, path.join(distDir, '404.html'));

        // 2. Pre-generate directories for known top-level SPA routes
        const routes = ['login', 'register', 'app', 'dashboard', 'compare', 'saved', 'admin', 'settings'];
        for (const route of routes) {
          const routeDir = path.join(distDir, route);
          if (!fs.existsSync(routeDir)) {
            fs.mkdirSync(routeDir, { recursive: true });
          }
          fs.copyFileSync(indexPath, path.join(routeDir, 'index.html'));
        }
      }
    }
  };
}

export default defineConfig({
  plugins: [react(), spaFallbackPlugin()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  },
  server: {
    port: 5173,
    host: true,
    watch: {
      usePolling: true,
    },
    proxy: {
      '/api': {
        target: backendTarget,
        changeOrigin: true,
        secure: false,
        ws: false,
        proxyTimeout: 0,
        configure: (proxy) => {
          proxy.on('proxyRes', (proxyRes) => {
            // Ensure SSE streams are not buffered
            if (proxyRes.headers['content-type']?.includes('text/event-stream')) {
              proxyRes.headers['x-accel-buffering'] = 'no';
            }
          });
        }
      }
    }
  }
})
