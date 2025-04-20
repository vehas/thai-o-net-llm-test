// @ts-check
import { defineConfig } from 'astro/config';
import tailwind from '@astrojs/tailwind';
//import icon from "astro-icon";

// https://astro.build/config
export default defineConfig({
  integrations: [
    tailwind(),
    // icon()
  ],
  output: 'static',
  build: {
    inlineStylesheets: 'auto'
  },
  site: 'https://vehas.github.io',
  base: '/thai-o-net-llm-test',
  vite: {
    build: {
      assetsInlineLimit: 4096,
      rollupOptions: {
        output: {
          manualChunks: undefined
        }
      }
    },
    optimizeDeps: {
      exclude: ['duckdb']
    }
  }
});
