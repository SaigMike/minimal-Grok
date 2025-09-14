import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// Vite configuration for the Grok chat front‑end.  The development server
// listens on port 5173 and binds to 0.0.0.0 so it is accessible to the host
// machine when running inside Docker.  Additional configuration can be
// specified via environment variables prefixed with `VITE_`.

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',
    port: 5173,
  },
});